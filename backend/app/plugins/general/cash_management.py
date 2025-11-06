"""
Cash Management Plugin

Features:
- Cash book (income/expenses)
- Change fund management
- Cash deposits (starting amount)
- Cash withdrawals (intermediate counts)
- Cash count (actual vs. expected)
- Difference tracking
- Shift-based accounting
- Z-report (end of day)
- Safe management (safe deposits)
- Coin/bill counting
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    select,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_db
from app.models.base import BaseModel as SQLBase
from app.models.base import TenantMixin
from app.models.user import User
from app.plugins.base import BasePlugin, PluginMetadata

logger = structlog.get_logger()


# ============================================================================
# Database Models
# ============================================================================


class CashRegister(SQLBase, TenantMixin):
    """Cash register balance tracking."""

    __tablename__ = "plugin_cash_registers"

    register_name = Column(String(100), nullable=False)
    register_number = Column(String(50), nullable=True)
    current_balance = Column(Numeric(10, 2), default=0)
    starting_float = Column(Numeric(10, 2), default=0)
    status = Column(String(20), default="closed")  # open, closed
    opened_at = Column(DateTime, nullable=True)
    opened_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    closed_at = Column(DateTime, nullable=True)
    closed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    is_active = Column(Boolean, default=True)


class CashTransaction(SQLBase, TenantMixin):
    """Individual cash transactions."""

    __tablename__ = "plugin_cash_transactions"

    register_id = Column(
        Integer, ForeignKey("plugin_cash_registers.id"), nullable=False
    )
    transaction_type = Column(
        String(20), nullable=False
    )  # deposit, withdrawal, sale, refund
    amount = Column(Numeric(10, 2), nullable=False)
    balance_before = Column(Numeric(10, 2), nullable=False)
    balance_after = Column(Numeric(10, 2), nullable=False)
    reference_type = Column(String(50), nullable=True)  # sale, manual, z_report
    reference_id = Column(Integer, nullable=True)
    description = Column(String(500), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)


class CashCount(SQLBase, TenantMixin):
    """Cash counting sessions."""

    __tablename__ = "plugin_cash_counts"

    register_id = Column(
        Integer, ForeignKey("plugin_cash_registers.id"), nullable=False
    )
    count_type = Column(String(20), nullable=False)  # opening, closing, intermediate
    expected_amount = Column(Numeric(10, 2), nullable=False)
    counted_amount = Column(Numeric(10, 2), nullable=False)
    difference = Column(Numeric(10, 2), nullable=False)
    count_time = Column(DateTime, nullable=False)
    notes = Column(String(1000), nullable=True)
    counted_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)


class CashCountDenomination(SQLBase, TenantMixin):
    """Detailed coin/bill counts."""

    __tablename__ = "plugin_cash_count_denominations"

    count_id = Column(Integer, ForeignKey("plugin_cash_counts.id"), nullable=False)
    denomination_type = Column(String(10), nullable=False)  # coin, bill
    denomination_value = Column(Numeric(10, 2), nullable=False)
    quantity = Column(Integer, nullable=False)
    total_value = Column(Numeric(10, 2), nullable=False)


class CashDeposit(SQLBase, TenantMixin):
    """Safe deposits."""

    __tablename__ = "plugin_cash_deposits"

    register_id = Column(
        Integer, ForeignKey("plugin_cash_registers.id"), nullable=False
    )
    amount = Column(Numeric(10, 2), nullable=False)
    deposit_type = Column(String(20), default="safe")  # safe, bank
    deposit_time = Column(DateTime, nullable=False)
    deposited_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    notes = Column(String(500), nullable=True)


class CashFloat(SQLBase, TenantMixin):
    """Change fund tracking."""

    __tablename__ = "plugin_cash_floats"

    register_id = Column(
        Integer, ForeignKey("plugin_cash_registers.id"), nullable=False
    )
    float_amount = Column(Numeric(10, 2), nullable=False)
    float_date = Column(DateTime, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)


# ============================================================================
# API Models (Pydantic)
# ============================================================================


class CashRegisterInfo(BaseModel):
    """Cash register information."""

    id: int
    register_name: str
    register_number: Optional[str]
    current_balance: Decimal
    starting_float: Decimal
    status: str
    opened_at: Optional[datetime]
    closed_at: Optional[datetime]
    is_active: bool

    class Config:
        from_attributes = True


class CashDepositRequest(BaseModel):
    """Request to deposit cash."""

    register_id: int
    amount: Decimal
    notes: Optional[str] = None


class CashWithdrawalRequest(BaseModel):
    """Request to withdraw cash."""

    register_id: int
    amount: Decimal
    description: Optional[str] = None


class CashCountRequest(BaseModel):
    """Request to perform cash count."""

    register_id: int
    count_type: str
    counted_amount: Decimal
    denominations: Optional[List[Dict[str, Any]]] = None
    notes: Optional[str] = None


class CashTransactionInfo(BaseModel):
    """Cash transaction information."""

    id: int
    register_id: int
    transaction_type: str
    amount: Decimal
    balance_before: Decimal
    balance_after: Decimal
    reference_type: Optional[str]
    description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class CashCountInfo(BaseModel):
    """Cash count information."""

    id: int
    register_id: int
    count_type: str
    expected_amount: Decimal
    counted_amount: Decimal
    difference: Decimal
    count_time: datetime
    notes: Optional[str]
    counted_by: Optional[int]

    class Config:
        from_attributes = True


class SafeDepositRequest(BaseModel):
    """Request to make safe deposit."""

    register_id: int
    amount: Decimal
    deposit_type: str = "safe"
    notes: Optional[str] = None


# ============================================================================
# Plugin Class
# ============================================================================


class CashManagementPlugin(BasePlugin):
    """
    Cash Management Plugin.

    Provides comprehensive cash handling and tracking.
    """

    def __init__(self):
        super().__init__()
        self.config = {
            "starting_float": 200.0,
            "max_cash_limit": 1000.0,
            "safe_deposit_threshold": 800.0,
            "enable_denomination_tracking": True,
            "require_manager_approval": False,
        }

    def get_metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        return PluginMetadata(
            name="cash_management",
            version="1.0.0",
            description="Cash register and safe management with detailed tracking",
            author="Stumpf.works",
            dependencies=[],
        )

    def get_name(self) -> str:
        """Get plugin name."""
        return "cash_management"

    def get_display_name(self) -> str:
        """Get plugin display name."""
        return "Kassenverwaltung"

    def get_description(self) -> str:
        """Get plugin description."""
        return "Kassenbuch und Bargeld-Verwaltung mit Kassensturz"

    def get_version(self) -> str:
        """Get plugin version."""
        return self.metadata.version

    def get_author(self) -> str:
        """Get plugin author."""
        return self.metadata.author

    def get_category(self) -> str:
        """Get plugin category."""
        return "general"

    def get_requires(self) -> List[str]:
        """Get plugin dependencies."""
        return self.metadata.dependencies

    def get_config_schema(self) -> Optional[Dict]:
        """Get plugin configuration schema."""
        return {
            "type": "object",
            "properties": {
                "starting_float": {
                    "type": "number",
                    "default": 200.0,
                    "minimum": 0,
                    "maximum": 10000,
                    "description": "Standard-Wechselgeld (EUR)",
                },
                "max_cash_limit": {
                    "type": "number",
                    "default": 1000.0,
                    "minimum": 0,
                    "maximum": 100000,
                    "description": "Max. Bargeld in Kasse (EUR)",
                },
                "safe_deposit_threshold": {
                    "type": "number",
                    "default": 800.0,
                    "minimum": 0,
                    "maximum": 100000,
                    "description": "Auto-Tresor ab (EUR)",
                },
                "enable_denomination_tracking": {
                    "type": "boolean",
                    "default": True,
                    "description": "Münz/Schein-Tracking aktivieren",
                },
                "require_manager_approval": {
                    "type": "boolean",
                    "default": False,
                    "description": "Manager-Freigabe für Entnahmen",
                },
            },
        }

    def configure(self, config: Dict):
        """Configure plugin with settings."""
        starting_float = config.get("starting_float", 200.0)
        if starting_float < 0 or starting_float > 10000:
            raise ValueError("starting_float must be between 0 and 10000")

        self.config.update(config)
        logger.info("cash_management_configured", config=self.config)

    def get_models(self) -> List[Any]:
        """Return database models."""
        return [
            CashRegister,
            CashTransaction,
            CashCount,
            CashCountDenomination,
            CashDeposit,
            CashFloat,
        ]

    async def on_enable(self):
        """Called when plugin is enabled."""
        logger.info("cash_management_enabled")

    async def on_disable(self):
        """Called when plugin is disabled."""
        logger.info("cash_management_disabled")

    def get_router(self) -> APIRouter:
        """Return API router with endpoints."""
        router = APIRouter(prefix="/cash", tags=["General - Cash Management"])

        # ============================================================================
        # Register Endpoints
        # ============================================================================

        @router.get("/balance")
        async def get_cash_balance(
            register_id: Optional[int] = Query(None),
            current_user: User = Depends(get_current_user),
            db: AsyncSession = Depends(get_db),
        ):
            """Get current cash balance."""
            if register_id:
                result = await db.execute(
                    select(CashRegister).where(
                        CashRegister.id == register_id,
                        CashRegister.tenant_id == current_user.tenant_id,
                    )
                )
                register = result.scalar_one_or_none()

                if not register:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Register not found",
                    )

                return {
                    "register_id": register.id,
                    "register_name": register.register_name,
                    "current_balance": float(register.current_balance),
                    "starting_float": float(register.starting_float),
                    "status": register.status,
                }

            # Get all open registers
            result = await db.execute(
                select(CashRegister).where(
                    CashRegister.tenant_id == current_user.tenant_id,
                    CashRegister.status == "open",
                )
            )
            registers = result.scalars().all()

            return {
                "registers": [
                    {
                        "id": r.id,
                        "register_name": r.register_name,
                        "current_balance": float(r.current_balance),
                    }
                    for r in registers
                ],
                "total_balance": sum(float(r.current_balance) for r in registers),
            }

        # ============================================================================
        # Transaction Endpoints
        # ============================================================================

        @router.post("/deposit")
        async def deposit_cash(
            request: CashDepositRequest,
            current_user: User = Depends(get_current_user),
            db: AsyncSession = Depends(get_db),
        ):
            """Deposit cash to register."""
            # Get register
            result = await db.execute(
                select(CashRegister).where(
                    CashRegister.id == request.register_id,
                    CashRegister.tenant_id == current_user.tenant_id,
                )
            )
            register = result.scalar_one_or_none()

            if not register:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Register not found",
                )

            # Create transaction
            balance_before = register.current_balance
            balance_after = balance_before + request.amount

            transaction = CashTransaction(
                tenant_id=current_user.tenant_id,
                register_id=request.register_id,
                transaction_type="deposit",
                amount=request.amount,
                balance_before=balance_before,
                balance_after=balance_after,
                reference_type="manual",
                description=request.notes or "Cash deposit",
                created_by=current_user.id,
            )
            db.add(transaction)

            # Update register balance
            register.current_balance = balance_after

            await db.commit()

            logger.info(
                "cash_deposited",
                register_id=request.register_id,
                amount=float(request.amount),
                user_id=current_user.id,
            )

            return {
                "register_id": request.register_id,
                "amount": float(request.amount),
                "balance_before": float(balance_before),
                "balance_after": float(balance_after),
                "message": "Cash deposited successfully",
            }

        @router.post("/withdrawal")
        async def withdraw_cash(
            request: CashWithdrawalRequest,
            current_user: User = Depends(get_current_user),
            db: AsyncSession = Depends(get_db),
        ):
            """Withdraw cash from register."""
            # Get register
            result = await db.execute(
                select(CashRegister).where(
                    CashRegister.id == request.register_id,
                    CashRegister.tenant_id == current_user.tenant_id,
                )
            )
            register = result.scalar_one_or_none()

            if not register:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Register not found",
                )

            # Check sufficient balance
            if register.current_balance < request.amount:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Insufficient cash in register",
                )

            # Create transaction
            balance_before = register.current_balance
            balance_after = balance_before - request.amount

            transaction = CashTransaction(
                tenant_id=current_user.tenant_id,
                register_id=request.register_id,
                transaction_type="withdrawal",
                amount=request.amount,
                balance_before=balance_before,
                balance_after=balance_after,
                reference_type="manual",
                description=request.description or "Cash withdrawal",
                created_by=current_user.id,
            )
            db.add(transaction)

            # Update register balance
            register.current_balance = balance_after

            await db.commit()

            logger.info(
                "cash_withdrawn",
                register_id=request.register_id,
                amount=float(request.amount),
                user_id=current_user.id,
            )

            return {
                "register_id": request.register_id,
                "amount": float(request.amount),
                "balance_before": float(balance_before),
                "balance_after": float(balance_after),
                "message": "Cash withdrawn successfully",
            }

        # ============================================================================
        # Cash Count Endpoints
        # ============================================================================

        @router.post("/count")
        async def perform_cash_count(
            request: CashCountRequest,
            current_user: User = Depends(get_current_user),
            db: AsyncSession = Depends(get_db),
        ):
            """Perform a cash count."""
            # Get register
            result = await db.execute(
                select(CashRegister).where(
                    CashRegister.id == request.register_id,
                    CashRegister.tenant_id == current_user.tenant_id,
                )
            )
            register = result.scalar_one_or_none()

            if not register:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Register not found",
                )

            # Calculate difference
            expected_amount = register.current_balance
            difference = request.counted_amount - expected_amount

            # Create count record
            count = CashCount(
                tenant_id=current_user.tenant_id,
                register_id=request.register_id,
                count_type=request.count_type,
                expected_amount=expected_amount,
                counted_amount=request.counted_amount,
                difference=difference,
                count_time=datetime.utcnow(),
                notes=request.notes,
                counted_by=current_user.id,
            )
            db.add(count)
            await db.flush()

            # Add denomination details if provided
            if request.denominations and self.config["enable_denomination_tracking"]:
                for denom_data in request.denominations:
                    denom = CashCountDenomination(
                        tenant_id=current_user.tenant_id,
                        count_id=count.id,
                        denomination_type=denom_data["type"],
                        denomination_value=Decimal(str(denom_data["value"])),
                        quantity=denom_data["quantity"],
                        total_value=Decimal(str(denom_data["value"]))
                        * denom_data["quantity"],
                    )
                    db.add(denom)

            # Adjust register balance if difference
            if difference != 0:
                # Create adjustment transaction
                transaction = CashTransaction(
                    tenant_id=current_user.tenant_id,
                    register_id=request.register_id,
                    transaction_type="adjustment",
                    amount=difference,
                    balance_before=expected_amount,
                    balance_after=request.counted_amount,
                    reference_type="cash_count",
                    reference_id=count.id,
                    description=f"Cash count adjustment: {request.count_type}",
                    created_by=current_user.id,
                )
                db.add(transaction)

                register.current_balance = request.counted_amount

            await db.commit()

            logger.info(
                "cash_count_performed",
                register_id=request.register_id,
                count_type=request.count_type,
                difference=float(difference),
                user_id=current_user.id,
            )

            return {
                "count_id": count.id,
                "register_id": request.register_id,
                "expected_amount": float(expected_amount),
                "counted_amount": float(request.counted_amount),
                "difference": float(difference),
                "message": "Cash count completed",
            }

        # ============================================================================
        # Transaction History
        # ============================================================================

        @router.get("/transactions", response_model=List[CashTransactionInfo])
        async def get_transactions(
            register_id: Optional[int] = Query(None),
            start_date: Optional[datetime] = Query(None),
            end_date: Optional[datetime] = Query(None),
            limit: int = Query(100, le=1000),
            current_user: User = Depends(get_current_user),
            db: AsyncSession = Depends(get_db),
        ):
            """Get cash transaction history."""
            query = select(CashTransaction).where(
                CashTransaction.tenant_id == current_user.tenant_id
            )

            if register_id:
                query = query.where(CashTransaction.register_id == register_id)

            if start_date:
                query = query.where(CashTransaction.created_at >= start_date)

            if end_date:
                query = query.where(CashTransaction.created_at <= end_date)

            query = query.order_by(CashTransaction.created_at.desc()).limit(limit)

            result = await db.execute(query)
            transactions = result.scalars().all()

            return [
                CashTransactionInfo(
                    id=t.id,
                    register_id=t.register_id,
                    transaction_type=t.transaction_type,
                    amount=t.amount,
                    balance_before=t.balance_before,
                    balance_after=t.balance_after,
                    reference_type=t.reference_type,
                    description=t.description,
                    created_at=t.created_at,
                )
                for t in transactions
            ]

        # ============================================================================
        # Z-Report Endpoint
        # ============================================================================

        @router.get("/z-report")
        async def generate_z_report(
            register_id: int,
            date: Optional[datetime] = Query(None),
            current_user: User = Depends(get_current_user),
            db: AsyncSession = Depends(get_db),
        ):
            """Generate end-of-day Z-report."""
            target_date = date or datetime.utcnow()
            start_of_day = target_date.replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            end_of_day = start_of_day + timedelta(days=1)

            # Get register
            register_result = await db.execute(
                select(CashRegister).where(
                    CashRegister.id == register_id,
                    CashRegister.tenant_id == current_user.tenant_id,
                )
            )
            register = register_result.scalar_one_or_none()

            if not register:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Register not found",
                )

            # Get transactions for the day
            transactions_result = await db.execute(
                select(CashTransaction).where(
                    CashTransaction.register_id == register_id,
                    CashTransaction.tenant_id == current_user.tenant_id,
                    CashTransaction.created_at >= start_of_day,
                    CashTransaction.created_at < end_of_day,
                )
            )
            transactions = transactions_result.scalars().all()

            # Calculate totals
            total_deposits = sum(
                float(t.amount) for t in transactions if t.transaction_type == "deposit"
            )
            total_withdrawals = sum(
                float(t.amount)
                for t in transactions
                if t.transaction_type == "withdrawal"
            )
            total_sales = sum(
                float(t.amount)
                for t in transactions
                if t.transaction_type == "sale" or t.reference_type == "sale"
            )

            # Get cash counts
            counts_result = await db.execute(
                select(CashCount).where(
                    CashCount.register_id == register_id,
                    CashCount.tenant_id == current_user.tenant_id,
                    CashCount.count_time >= start_of_day,
                    CashCount.count_time < end_of_day,
                )
            )
            counts = counts_result.scalars().all()

            return {
                "register_id": register_id,
                "register_name": register.register_name,
                "report_date": target_date.date().isoformat(),
                "starting_balance": float(register.starting_float),
                "ending_balance": float(register.current_balance),
                "summary": {
                    "total_transactions": len(transactions),
                    "total_deposits": total_deposits,
                    "total_withdrawals": total_withdrawals,
                    "total_sales": total_sales,
                    "net_change": total_deposits - total_withdrawals,
                },
                "cash_counts": [
                    {
                        "count_type": c.count_type,
                        "expected": float(c.expected_amount),
                        "counted": float(c.counted_amount),
                        "difference": float(c.difference),
                        "time": c.count_time.isoformat(),
                    }
                    for c in counts
                ],
            }

        # ============================================================================
        # Safe Deposit Endpoint
        # ============================================================================

        @router.post("/safe-deposit")
        async def make_safe_deposit(
            request: SafeDepositRequest,
            current_user: User = Depends(get_current_user),
            db: AsyncSession = Depends(get_db),
        ):
            """Make a safe deposit."""
            # Get register
            result = await db.execute(
                select(CashRegister).where(
                    CashRegister.id == request.register_id,
                    CashRegister.tenant_id == current_user.tenant_id,
                )
            )
            register = result.scalar_one_or_none()

            if not register:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Register not found",
                )

            # Check sufficient balance
            if register.current_balance < request.amount:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Insufficient cash in register",
                )

            # Create safe deposit record
            deposit = CashDeposit(
                tenant_id=current_user.tenant_id,
                register_id=request.register_id,
                amount=request.amount,
                deposit_type=request.deposit_type,
                deposit_time=datetime.utcnow(),
                deposited_by=current_user.id,
                notes=request.notes,
            )
            db.add(deposit)

            # Create transaction
            balance_before = register.current_balance
            balance_after = balance_before - request.amount

            transaction = CashTransaction(
                tenant_id=current_user.tenant_id,
                register_id=request.register_id,
                transaction_type="withdrawal",
                amount=request.amount,
                balance_before=balance_before,
                balance_after=balance_after,
                reference_type="safe_deposit",
                description=f"Safe deposit: {request.deposit_type}",
                created_by=current_user.id,
            )
            db.add(transaction)

            # Update register
            register.current_balance = balance_after

            await db.commit()

            logger.info(
                "safe_deposit_made",
                register_id=request.register_id,
                amount=float(request.amount),
                user_id=current_user.id,
            )

            return {
                "deposit_id": deposit.id,
                "amount": float(request.amount),
                "balance_after": float(balance_after),
                "message": "Safe deposit completed",
            }

        # ============================================================================
        # Denominations Endpoint
        # ============================================================================

        @router.get("/denominations")
        async def get_denomination_breakdown(
            count_id: int,
            current_user: User = Depends(get_current_user),
            db: AsyncSession = Depends(get_db),
        ):
            """Get coin/bill breakdown for a cash count."""
            result = await db.execute(
                select(CashCountDenomination).where(
                    CashCountDenomination.count_id == count_id,
                    CashCountDenomination.tenant_id == current_user.tenant_id,
                )
            )
            denominations = result.scalars().all()

            return {
                "count_id": count_id,
                "denominations": [
                    {
                        "type": d.denomination_type,
                        "value": float(d.denomination_value),
                        "quantity": d.quantity,
                        "total": float(d.total_value),
                    }
                    for d in denominations
                ],
                "total": sum(float(d.total_value) for d in denominations),
            }

        return router


# ============================================================================
# Plugin Instance (for auto-discovery)
# ============================================================================

plugin = CashManagementPlugin()

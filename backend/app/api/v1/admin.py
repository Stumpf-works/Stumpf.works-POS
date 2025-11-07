"""
Admin API Endpoints
Dashboard, user management, and system administration
"""

from datetime import datetime, timedelta
from typing import List, Optional

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, require_admin
from app.core.database import get_db
from app.models.product import Product
from app.models.tenant import Tenant
from app.models.transaction import (
    PaymentMethod,
    Transaction,
    TransactionItem,
    TransactionStatus,
)
from app.models.user import User, UserRole

logger = structlog.get_logger()
router = APIRouter(prefix="/admin", tags=["Admin"])


# Dashboard endpoints


class DashboardStats(BaseModel):
    today_sales: float
    today_transactions: int
    today_average_basket: float
    month_sales: float
    month_transactions: int
    active_products: int
    low_stock_products: int
    pending_tse_signatures: int


class RecentTransactionResponse(BaseModel):
    id: int
    receipt_number: str
    total: float
    payment_method: str
    completed_at: datetime
    is_tse_signed: bool


@router.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get dashboard statistics."""
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    month_start = datetime.now().replace(
        day=1, hour=0, minute=0, second=0, microsecond=0
    )

    # Today's sales
    today_result = await db.execute(
        select(
            func.coalesce(func.sum(Transaction.total), 0), func.count(Transaction.id)
        ).where(
            and_(
                Transaction.tenant_id == current_user.tenant_id,
                Transaction.completed_at >= today_start,
                Transaction.status == TransactionStatus.COMPLETED,
            )
        )
    )
    today_sales, today_count = today_result.first()

    # Month's sales
    month_result = await db.execute(
        select(
            func.coalesce(func.sum(Transaction.total), 0), func.count(Transaction.id)
        ).where(
            and_(
                Transaction.tenant_id == current_user.tenant_id,
                Transaction.completed_at >= month_start,
                Transaction.status == TransactionStatus.COMPLETED,
            )
        )
    )
    month_sales, month_count = month_result.first()

    # Active products
    active_products_result = await db.execute(
        select(func.count(Product.id)).where(
            and_(Product.tenant_id == current_user.tenant_id, Product.is_active == True)
        )
    )
    active_products = active_products_result.scalar()

    # Low stock products
    low_stock_result = await db.execute(
        select(func.count(Product.id)).where(
            and_(
                Product.tenant_id == current_user.tenant_id,
                Product.is_active == True,
                Product.stock_quantity < 10,
            )
        )
    )
    low_stock_products = low_stock_result.scalar()

    # Pending TSE signatures
    pending_tse_result = await db.execute(
        select(func.count(Transaction.id)).where(
            and_(
                Transaction.tenant_id == current_user.tenant_id,
                Transaction.status == TransactionStatus.COMPLETED,
                Transaction.is_tse_signed == False,
            )
        )
    )
    pending_tse = pending_tse_result.scalar()

    return DashboardStats(
        today_sales=float(today_sales or 0),
        today_transactions=today_count or 0,
        today_average_basket=float(today_sales / today_count) if today_count > 0 else 0,
        month_sales=float(month_sales or 0),
        month_transactions=month_count or 0,
        active_products=active_products or 0,
        low_stock_products=low_stock_products or 0,
        pending_tse_signatures=pending_tse or 0,
    )


@router.get(
    "/dashboard/recent-transactions", response_model=List[RecentTransactionResponse]
)
async def get_recent_transactions(
    limit: int = Query(10, le=50),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get recent transactions."""
    result = await db.execute(
        select(Transaction)
        .where(
            and_(
                Transaction.tenant_id == current_user.tenant_id,
                Transaction.status == TransactionStatus.COMPLETED,
            )
        )
        .order_by(Transaction.completed_at.desc())
        .limit(limit)
    )
    transactions = result.scalars().all()

    return [
        RecentTransactionResponse(
            id=txn.id,
            receipt_number=txn.receipt_number,
            total=txn.total,
            payment_method=txn.payment_method.value,
            completed_at=txn.completed_at,
            is_tse_signed=txn.is_tse_signed or False,
        )
        for txn in transactions
    ]


# User management endpoints


class UserResponse(BaseModel):
    id: int
    username: str
    email: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    role: str
    pin_enabled: bool
    is_active: bool
    created_at: datetime


class CreateUserRequest(BaseModel):
    username: str
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: UserRole
    password: Optional[str] = None
    pin: Optional[str] = None


class UpdateUserRequest(BaseModel):
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


@router.get("/users", response_model=List[UserResponse])
async def list_users(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """List all users (admin only)."""
    result = await db.execute(
        select(User)
        .where(User.tenant_id == current_user.tenant_id)
        .order_by(User.created_at.desc())
    )
    users = result.scalars().all()

    return [
        UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            role=user.role.value,
            pin_enabled=user.pin_hash is not None,
            is_active=user.is_active,
            created_at=user.created_at,
        )
        for user in users
    ]


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: CreateUserRequest,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Create new user (admin only)."""
    from app.core.security import get_password_hash, get_pin_hash

    # Check if username exists
    result = await db.execute(
        select(User).where(
            and_(
                User.tenant_id == current_user.tenant_id,
                User.username == user_data.username,
            )
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists"
        )

    # Create user
    new_user = User(
        tenant_id=current_user.tenant_id,
        username=user_data.username,
        email=user_data.email,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        role=user_data.role,
        password_hash=(
            get_password_hash(user_data.password) if user_data.password else None
        ),
        pin_hash=get_pin_hash(user_data.pin) if user_data.pin else None,
        is_active=True,
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    logger.info(
        "user_created",
        user_id=new_user.id,
        username=new_user.username,
        created_by=current_user.id,
    )

    return UserResponse(
        id=new_user.id,
        username=new_user.username,
        email=new_user.email,
        first_name=new_user.first_name,
        last_name=new_user.last_name,
        role=new_user.role.value,
        pin_enabled=new_user.pin_hash is not None,
        is_active=new_user.is_active,
        created_at=new_user.created_at,
    )


@router.patch("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UpdateUserRequest,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Update user (admin only)."""
    result = await db.execute(
        select(User).where(
            and_(User.id == user_id, User.tenant_id == current_user.tenant_id)
        )
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Update fields
    if user_data.email is not None:
        user.email = user_data.email
    if user_data.first_name is not None:
        user.first_name = user_data.first_name
    if user_data.last_name is not None:
        user.last_name = user_data.last_name
    if user_data.role is not None:
        user.role = user_data.role
    if user_data.is_active is not None:
        user.is_active = user_data.is_active

    await db.commit()
    await db.refresh(user)

    logger.info(
        "user_updated",
        user_id=user.id,
        updated_by=current_user.id,
    )

    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role.value,
        pin_enabled=user.pin_hash is not None,
        is_active=user.is_active,
        created_at=user.created_at,
    )


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Delete user (admin only)."""
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account",
        )

    result = await db.execute(
        select(User).where(
            and_(User.id == user_id, User.tenant_id == current_user.tenant_id)
        )
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    await db.delete(user)
    await db.commit()

    logger.info(
        "user_deleted",
        user_id=user_id,
        deleted_by=current_user.id,
    )


# Reports endpoints


class SalesReport(BaseModel):
    total_sales: float
    total_transactions: int
    average_basket: float
    sales_by_payment_method: dict
    sales_by_day: List[dict]
    top_products: List[dict]
    sales_by_hour: List[dict]


@router.get("/reports/sales", response_model=SalesReport)
async def get_sales_report(
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    group_by: str = Query("day", regex="^(day|week|month)$"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get sales report."""
    # Total sales and transactions
    total_result = await db.execute(
        select(
            func.coalesce(func.sum(Transaction.total), 0), func.count(Transaction.id)
        ).where(
            and_(
                Transaction.tenant_id == current_user.tenant_id,
                Transaction.completed_at >= start_date,
                Transaction.completed_at <= end_date,
                Transaction.status == TransactionStatus.COMPLETED,
            )
        )
    )
    total_sales, total_count = total_result.first()

    # Sales by payment method
    payment_result = await db.execute(
        select(
            Transaction.payment_method, func.coalesce(func.sum(Transaction.total), 0)
        )
        .where(
            and_(
                Transaction.tenant_id == current_user.tenant_id,
                Transaction.completed_at >= start_date,
                Transaction.completed_at <= end_date,
                Transaction.status == TransactionStatus.COMPLETED,
            )
        )
        .group_by(Transaction.payment_method)
    )
    sales_by_payment = {
        PaymentMethod.CASH.value: 0,
        PaymentMethod.CARD.value: 0,
        PaymentMethod.SUMUP.value: 0,
    }
    for method, amount in payment_result:
        sales_by_payment[method.value] = float(amount)

    # Sales by day (simplified)
    day_result = await db.execute(
        select(
            func.date(Transaction.completed_at).label("date"),
            func.coalesce(func.sum(Transaction.total), 0).label("sales"),
            func.count(Transaction.id).label("transactions"),
        )
        .where(
            and_(
                Transaction.tenant_id == current_user.tenant_id,
                Transaction.completed_at >= start_date,
                Transaction.completed_at <= end_date,
                Transaction.status == TransactionStatus.COMPLETED,
            )
        )
        .group_by(func.date(Transaction.completed_at))
        .order_by(func.date(Transaction.completed_at))
    )
    sales_by_day = [
        {
            "date": str(row.date),
            "sales": float(row.sales),
            "transactions": row.transactions,
        }
        for row in day_result
    ]

    # Top products
    top_products_result = await db.execute(
        select(
            TransactionItem.product_id,
            TransactionItem.product_name,
            func.sum(TransactionItem.quantity).label("quantity_sold"),
            func.sum(TransactionItem.total).label("total_sales"),
        )
        .join(Transaction)
        .where(
            and_(
                Transaction.tenant_id == current_user.tenant_id,
                Transaction.completed_at >= start_date,
                Transaction.completed_at <= end_date,
                Transaction.status == TransactionStatus.COMPLETED,
            )
        )
        .group_by(TransactionItem.product_id, TransactionItem.product_name)
        .order_by(func.sum(TransactionItem.total).desc())
        .limit(10)
    )
    top_products = [
        {
            "product_id": row.product_id,
            "product_name": row.product_name,
            "quantity_sold": int(row.quantity_sold),
            "total_sales": float(row.total_sales),
        }
        for row in top_products_result
    ]

    # Sales by hour
    hour_result = await db.execute(
        select(
            func.extract("hour", Transaction.completed_at).label("hour"),
            func.coalesce(func.sum(Transaction.total), 0).label("sales"),
            func.count(Transaction.id).label("transactions"),
        )
        .where(
            and_(
                Transaction.tenant_id == current_user.tenant_id,
                Transaction.completed_at >= start_date,
                Transaction.completed_at <= end_date,
                Transaction.status == TransactionStatus.COMPLETED,
            )
        )
        .group_by(func.extract("hour", Transaction.completed_at))
        .order_by(func.extract("hour", Transaction.completed_at))
    )
    sales_by_hour = [
        {
            "hour": int(row.hour),
            "sales": float(row.sales),
            "transactions": row.transactions,
        }
        for row in hour_result
    ]

    return SalesReport(
        total_sales=float(total_sales or 0),
        total_transactions=total_count or 0,
        average_basket=float(total_sales / total_count) if total_count > 0 else 0,
        sales_by_payment_method=sales_by_payment,
        sales_by_day=sales_by_day,
        top_products=top_products,
        sales_by_hour=sales_by_hour,
    )


# Settings endpoints


class TenantSettingsResponse(BaseModel):
    name: str
    address_street: Optional[str]
    address_postal_code: Optional[str]
    address_city: Optional[str]
    address_country: Optional[str]
    tax_id: Optional[str]
    vat_id: Optional[str]
    sumup_enabled: bool
    sumup_merchant_code: Optional[str]
    tse_enabled: bool
    fiskaly_api_key: Optional[str]
    fiskaly_api_secret: Optional[str]
    fiskaly_tss_id: Optional[str]


@router.get("/settings/tenant", response_model=TenantSettingsResponse)
async def get_tenant_settings(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Get tenant settings (admin only)."""
    result = await db.execute(
        select(Tenant).where(Tenant.slug == current_user.tenant_id)
    )
    tenant = result.scalar_one_or_none()

    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found"
        )

    return TenantSettingsResponse(
        name=tenant.name,
        address_street=tenant.address_street,
        address_postal_code=tenant.address_postal_code,
        address_city=tenant.address_city,
        address_country=tenant.address_country,
        tax_id=tenant.tax_id,
        vat_id=tenant.vat_id,
        sumup_enabled=tenant.sumup_enabled or False,
        sumup_merchant_code=tenant.sumup_merchant_code,
        tse_enabled=tenant.tse_enabled or False,
        fiskaly_api_key=tenant.fiskaly_api_key if tenant.fiskaly_api_key else None,
        fiskaly_api_secret="***" if tenant.fiskaly_api_secret else None,
        fiskaly_tss_id=tenant.fiskaly_tss_id,
    )


@router.patch("/settings/tenant")
async def update_tenant_settings(
    settings: dict,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Update tenant settings (admin only)."""
    result = await db.execute(
        select(Tenant).where(Tenant.slug == current_user.tenant_id)
    )
    tenant = result.scalar_one_or_none()

    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found"
        )

    # Update allowed fields
    allowed_fields = {
        "name",
        "address_street",
        "address_postal_code",
        "address_city",
        "address_country",
        "tax_id",
        "vat_id",
        "sumup_enabled",
        "sumup_merchant_code",
        "tse_enabled",
        "fiskaly_api_key",
        "fiskaly_api_secret",
        "fiskaly_tss_id",
    }

    for field, value in settings.items():
        if field in allowed_fields:
            setattr(tenant, field, value)

    await db.commit()
    await db.refresh(tenant)

    logger.info(
        "tenant_settings_updated",
        tenant_id=tenant.slug,
        updated_by=current_user.id,
    )

    return {"message": "Settings updated successfully"}

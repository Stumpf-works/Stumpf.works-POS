"""
Inventory Management Pro Plugin

Features:
- Stock level tracking with min/max levels
- Automatic reorder suggestions
- Supplier management
- Stock alerts (email/notification)
- Inventory counts
- Stock movement tracking (in, out, adjustment)
- Cost calculation
- Barcode generation
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
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


class Supplier(SQLBase, TenantMixin):
    """Supplier model for inventory management."""

    __tablename__ = "plugin_inventory_suppliers"

    name = Column(String(200), nullable=False)
    code = Column(String(50), nullable=True)
    contact_person = Column(String(200), nullable=True)
    email = Column(String(200), nullable=True)
    phone = Column(String(50), nullable=True)
    address = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    notes = Column(String(1000), nullable=True)


class StockLevel(SQLBase, TenantMixin):
    """Current stock levels for products."""

    __tablename__ = "plugin_inventory_stock_levels"

    product_id = Column(Integer, nullable=False)
    quantity = Column(Numeric(10, 2), nullable=False, default=0)
    min_level = Column(Numeric(10, 2), nullable=True)
    max_level = Column(Numeric(10, 2), nullable=True)
    reorder_point = Column(Numeric(10, 2), nullable=True)
    reorder_quantity = Column(Numeric(10, 2), nullable=True)
    unit_cost = Column(Numeric(10, 2), nullable=True)
    supplier_id = Column(
        Integer, ForeignKey("plugin_inventory_suppliers.id"), nullable=True
    )
    barcode = Column(String(100), nullable=True)
    location = Column(String(200), nullable=True)


class StockMovement(SQLBase, TenantMixin):
    """History of all stock movements."""

    __tablename__ = "plugin_inventory_movements"

    product_id = Column(Integer, nullable=False)
    movement_type = Column(String(20), nullable=False)  # in, out, adjustment
    quantity = Column(Numeric(10, 2), nullable=False)
    quantity_before = Column(Numeric(10, 2), nullable=False)
    quantity_after = Column(Numeric(10, 2), nullable=False)
    unit_cost = Column(Numeric(10, 2), nullable=True)
    reference_type = Column(
        String(50), nullable=True
    )  # purchase_order, sale, count, manual
    reference_id = Column(Integer, nullable=True)
    notes = Column(String(1000), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)


class PurchaseOrder(SQLBase, TenantMixin):
    """Purchase orders to suppliers."""

    __tablename__ = "plugin_inventory_purchase_orders"

    order_number = Column(String(50), nullable=False, unique=True)
    supplier_id = Column(
        Integer, ForeignKey("plugin_inventory_suppliers.id"), nullable=False
    )
    status = Column(String(20), default="draft")  # draft, sent, received, cancelled
    order_date = Column(DateTime, nullable=False)
    expected_delivery = Column(DateTime, nullable=True)
    actual_delivery = Column(DateTime, nullable=True)
    total_amount = Column(Numeric(10, 2), default=0)
    notes = Column(String(1000), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)


class PurchaseOrderItem(SQLBase, TenantMixin):
    """Line items for purchase orders."""

    __tablename__ = "plugin_inventory_purchase_order_items"

    purchase_order_id = Column(
        Integer, ForeignKey("plugin_inventory_purchase_orders.id"), nullable=False
    )
    product_id = Column(Integer, nullable=False)
    quantity = Column(Numeric(10, 2), nullable=False)
    unit_cost = Column(Numeric(10, 2), nullable=False)
    total_cost = Column(Numeric(10, 2), nullable=False)
    received_quantity = Column(Numeric(10, 2), default=0)


class InventoryCount(SQLBase, TenantMixin):
    """Inventory count sessions."""

    __tablename__ = "plugin_inventory_counts"

    count_number = Column(String(50), nullable=False, unique=True)
    status = Column(
        String(20), default="in_progress"
    )  # in_progress, completed, cancelled
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    notes = Column(String(1000), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)


class InventoryCountItem(SQLBase, TenantMixin):
    """Individual items counted during inventory."""

    __tablename__ = "plugin_inventory_count_items"

    count_id = Column(Integer, ForeignKey("plugin_inventory_counts.id"), nullable=False)
    product_id = Column(Integer, nullable=False)
    expected_quantity = Column(Numeric(10, 2), nullable=False)
    counted_quantity = Column(Numeric(10, 2), nullable=False)
    difference = Column(Numeric(10, 2), nullable=False)
    notes = Column(String(500), nullable=True)


# ============================================================================
# API Models (Pydantic)
# ============================================================================


class SupplierCreate(BaseModel):
    """Request to create a supplier."""

    name: str
    code: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None


class SupplierInfo(BaseModel):
    """Supplier information response."""

    id: int
    name: str
    code: Optional[str]
    contact_person: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    address: Optional[str]
    is_active: bool

    class Config:
        from_attributes = True


class StockLevelInfo(BaseModel):
    """Stock level information."""

    id: int
    product_id: int
    quantity: Decimal
    min_level: Optional[Decimal]
    max_level: Optional[Decimal]
    reorder_point: Optional[Decimal]
    reorder_quantity: Optional[Decimal]
    unit_cost: Optional[Decimal]
    supplier_id: Optional[int]
    barcode: Optional[str]
    location: Optional[str]
    is_low_stock: bool = False

    class Config:
        from_attributes = True


class StockAdjustment(BaseModel):
    """Request to adjust stock."""

    product_id: int
    quantity: Decimal
    movement_type: str = Field(..., pattern="^(in|out|adjustment)$")
    unit_cost: Optional[Decimal] = None
    notes: Optional[str] = None


class StockMovementInfo(BaseModel):
    """Stock movement information."""

    id: int
    product_id: int
    movement_type: str
    quantity: Decimal
    quantity_before: Decimal
    quantity_after: Decimal
    unit_cost: Optional[Decimal]
    reference_type: Optional[str]
    reference_id: Optional[int]
    notes: Optional[str]
    created_at: datetime
    created_by: Optional[int]

    class Config:
        from_attributes = True


class PurchaseOrderCreate(BaseModel):
    """Request to create a purchase order."""

    supplier_id: int
    order_date: datetime
    expected_delivery: Optional[datetime] = None
    notes: Optional[str] = None
    items: List[Dict[str, Any]]  # [{product_id, quantity, unit_cost}]


class PurchaseOrderInfo(BaseModel):
    """Purchase order information."""

    id: int
    order_number: str
    supplier_id: int
    supplier_name: str
    status: str
    order_date: datetime
    expected_delivery: Optional[datetime]
    actual_delivery: Optional[datetime]
    total_amount: Decimal
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class InventoryCountCreate(BaseModel):
    """Request to start an inventory count."""

    notes: Optional[str] = None


class InventoryCountSubmit(BaseModel):
    """Submit count results."""

    items: List[Dict[str, Any]]  # [{product_id, counted_quantity}]


class InventoryCountInfo(BaseModel):
    """Inventory count information."""

    id: int
    count_number: str
    status: str
    start_time: datetime
    end_time: Optional[datetime]
    notes: Optional[str]
    total_items: int = 0
    total_differences: int = 0

    class Config:
        from_attributes = True


# ============================================================================
# Plugin Class
# ============================================================================


class InventoryManagementPlugin(BasePlugin):
    """
    Inventory Management Pro Plugin.

    Provides comprehensive inventory management for retail businesses.
    """

    def __init__(self):
        super().__init__()
        self.config = {
            "enable_auto_reorder": True,
            "low_stock_threshold_percentage": 20,
            "enable_email_alerts": False,
            "default_supplier_id": None,
        }

    def get_metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        return PluginMetadata(
            name="inventory_management",
            version="1.0.0",
            description="Advanced inventory management with stock tracking and reordering",
            author="Stumpf.works",
            dependencies=[],
        )

    def get_name(self) -> str:
        """Get plugin name."""
        return "inventory_management"

    def get_display_name(self) -> str:
        """Get plugin display name."""
        return "Bestandsverwaltung Pro"

    def get_description(self) -> str:
        """Get plugin description."""
        return (
            "Erweiterte Bestandsverwaltung mit automatischen Bestellvorschlägen "
            "und Lieferantenverwaltung"
        )

    def get_version(self) -> str:
        """Get plugin version."""
        return self.metadata.version

    def get_author(self) -> str:
        """Get plugin author."""
        return self.metadata.author

    def get_category(self) -> str:
        """Get plugin category."""
        return "retail"

    def get_requires(self) -> List[str]:
        """Get plugin dependencies."""
        return self.metadata.dependencies

    def get_config_schema(self) -> Optional[Dict]:
        """Get plugin configuration schema."""
        return {
            "type": "object",
            "properties": {
                "enable_auto_reorder": {
                    "type": "boolean",
                    "default": True,
                    "description": "Automatische Bestellvorschläge aktivieren",
                },
                "low_stock_threshold_percentage": {
                    "type": "integer",
                    "default": 20,
                    "minimum": 0,
                    "maximum": 100,
                    "description": "Warnschwelle für niedrigen Bestand (%)",
                },
                "enable_email_alerts": {
                    "type": "boolean",
                    "default": False,
                    "description": "E-Mail-Benachrichtigungen bei niedrigem Bestand",
                },
                "default_supplier_id": {
                    "type": ["integer", "null"],
                    "default": None,
                    "description": "Standard-Lieferant ID",
                },
            },
        }

    def configure(self, config: Dict):
        """Configure plugin with settings."""
        threshold = config.get("low_stock_threshold_percentage", 20)
        if threshold < 0 or threshold > 100:
            raise ValueError("Threshold must be between 0 and 100")

        self.config.update(config)
        logger.info("inventory_management_configured", config=self.config)

    def get_models(self) -> List[Any]:
        """Return database models."""
        return [
            Supplier,
            StockLevel,
            StockMovement,
            PurchaseOrder,
            PurchaseOrderItem,
            InventoryCount,
            InventoryCountItem,
        ]

    async def on_enable(self):
        """Called when plugin is enabled."""
        logger.info("inventory_management_enabled")

    async def on_disable(self):
        """Called when plugin is disabled."""
        logger.info("inventory_management_disabled")

    def get_router(self) -> APIRouter:
        """Return API router with endpoints."""
        router = APIRouter(prefix="/inventory", tags=["Retail - Inventory Management"])

        # ============================================================================
        # Stock Endpoints
        # ============================================================================

        @router.get("/stock", response_model=List[StockLevelInfo])
        async def get_stock_levels(
            low_stock_only: bool = Query(False),
            current_user: User = Depends(get_current_user),
            db: AsyncSession = Depends(get_db),
        ):
            """Get stock levels for all products."""
            result = await db.execute(
                select(StockLevel).where(StockLevel.tenant_id == current_user.tenant_id)
            )
            stock_levels = result.scalars().all()

            stock_info = []
            for stock in stock_levels:
                is_low = False
                if stock.reorder_point and stock.quantity <= stock.reorder_point:
                    is_low = True

                if low_stock_only and not is_low:
                    continue

                stock_info.append(
                    StockLevelInfo(
                        id=stock.id,
                        product_id=stock.product_id,
                        quantity=stock.quantity,
                        min_level=stock.min_level,
                        max_level=stock.max_level,
                        reorder_point=stock.reorder_point,
                        reorder_quantity=stock.reorder_quantity,
                        unit_cost=stock.unit_cost,
                        supplier_id=stock.supplier_id,
                        barcode=stock.barcode,
                        location=stock.location,
                        is_low_stock=is_low,
                    )
                )

            return stock_info

        @router.post("/stock/adjust")
        async def adjust_stock(
            request: StockAdjustment,
            current_user: User = Depends(get_current_user),
            db: AsyncSession = Depends(get_db),
        ):
            """Adjust stock level for a product."""
            # Get or create stock level
            result = await db.execute(
                select(StockLevel).where(
                    StockLevel.tenant_id == current_user.tenant_id,
                    StockLevel.product_id == request.product_id,
                )
            )
            stock = result.scalar_one_or_none()

            if not stock:
                # Create new stock level
                stock = StockLevel(
                    tenant_id=current_user.tenant_id,
                    product_id=request.product_id,
                    quantity=0,
                )
                db.add(stock)
                await db.flush()

            # Calculate new quantity
            quantity_before = stock.quantity
            if request.movement_type == "in":
                quantity_after = quantity_before + request.quantity
            elif request.movement_type == "out":
                quantity_after = quantity_before - request.quantity
            else:  # adjustment
                quantity_after = request.quantity

            # Update stock
            stock.quantity = quantity_after
            if request.unit_cost:
                stock.unit_cost = request.unit_cost

            # Create movement record
            movement = StockMovement(
                tenant_id=current_user.tenant_id,
                product_id=request.product_id,
                movement_type=request.movement_type,
                quantity=request.quantity,
                quantity_before=quantity_before,
                quantity_after=quantity_after,
                unit_cost=request.unit_cost,
                reference_type="manual",
                notes=request.notes,
                created_by=current_user.id,
            )
            db.add(movement)

            await db.commit()
            await db.refresh(stock)

            logger.info(
                "stock_adjusted",
                product_id=request.product_id,
                movement_type=request.movement_type,
                quantity=request.quantity,
                user_id=current_user.id,
            )

            return {
                "message": "Stock adjusted successfully",
                "product_id": request.product_id,
                "quantity_before": float(quantity_before),
                "quantity_after": float(quantity_after),
            }

        @router.get("/movements", response_model=List[StockMovementInfo])
        async def get_stock_movements(
            product_id: Optional[int] = Query(None),
            limit: int = Query(100, le=1000),
            current_user: User = Depends(get_current_user),
            db: AsyncSession = Depends(get_db),
        ):
            """Get stock movement history."""
            query = select(StockMovement).where(
                StockMovement.tenant_id == current_user.tenant_id
            )

            if product_id:
                query = query.where(StockMovement.product_id == product_id)

            query = query.order_by(StockMovement.created_at.desc()).limit(limit)

            result = await db.execute(query)
            movements = result.scalars().all()

            return [
                StockMovementInfo(
                    id=m.id,
                    product_id=m.product_id,
                    movement_type=m.movement_type,
                    quantity=m.quantity,
                    quantity_before=m.quantity_before,
                    quantity_after=m.quantity_after,
                    unit_cost=m.unit_cost,
                    reference_type=m.reference_type,
                    reference_id=m.reference_id,
                    notes=m.notes,
                    created_at=m.created_at,
                    created_by=m.created_by,
                )
                for m in movements
            ]

        @router.get("/low-stock")
        async def get_low_stock_items(
            current_user: User = Depends(get_current_user),
            db: AsyncSession = Depends(get_db),
        ):
            """Get products with low stock."""
            result = await db.execute(
                select(StockLevel).where(StockLevel.tenant_id == current_user.tenant_id)
            )
            stock_levels = result.scalars().all()

            low_stock_items = []
            for stock in stock_levels:
                if stock.reorder_point and stock.quantity <= stock.reorder_point:
                    low_stock_items.append(
                        {
                            "product_id": stock.product_id,
                            "quantity": float(stock.quantity),
                            "reorder_point": float(stock.reorder_point),
                            "reorder_quantity": (
                                float(stock.reorder_quantity)
                                if stock.reorder_quantity
                                else None
                            ),
                            "supplier_id": stock.supplier_id,
                        }
                    )

            return {
                "count": len(low_stock_items),
                "items": low_stock_items,
            }

        # ============================================================================
        # Supplier Endpoints
        # ============================================================================

        @router.get("/suppliers", response_model=List[SupplierInfo])
        async def list_suppliers(
            current_user: User = Depends(get_current_user),
            db: AsyncSession = Depends(get_db),
        ):
            """List all suppliers."""
            result = await db.execute(
                select(Supplier).where(
                    Supplier.tenant_id == current_user.tenant_id,
                    Supplier.is_active == True,  # noqa
                )
            )
            suppliers = result.scalars().all()

            return [
                SupplierInfo(
                    id=s.id,
                    name=s.name,
                    code=s.code,
                    contact_person=s.contact_person,
                    email=s.email,
                    phone=s.phone,
                    address=s.address,
                    is_active=s.is_active,
                )
                for s in suppliers
            ]

        @router.post(
            "/suppliers",
            response_model=SupplierInfo,
            status_code=status.HTTP_201_CREATED,
        )
        async def create_supplier(
            request: SupplierCreate,
            current_user: User = Depends(get_current_user),
            db: AsyncSession = Depends(get_db),
        ):
            """Create a new supplier."""
            supplier = Supplier(
                tenant_id=current_user.tenant_id,
                name=request.name,
                code=request.code,
                contact_person=request.contact_person,
                email=request.email,
                phone=request.phone,
                address=request.address,
                notes=request.notes,
            )
            db.add(supplier)
            await db.commit()
            await db.refresh(supplier)

            logger.info("supplier_created", supplier_id=supplier.id, name=request.name)

            return SupplierInfo(
                id=supplier.id,
                name=supplier.name,
                code=supplier.code,
                contact_person=supplier.contact_person,
                email=supplier.email,
                phone=supplier.phone,
                address=supplier.address,
                is_active=supplier.is_active,
            )

        # ============================================================================
        # Purchase Order Endpoints
        # ============================================================================

        @router.post("/purchase-orders", status_code=status.HTTP_201_CREATED)
        async def create_purchase_order(
            request: PurchaseOrderCreate,
            current_user: User = Depends(get_current_user),
            db: AsyncSession = Depends(get_db),
        ):
            """Create a new purchase order."""
            # Verify supplier exists
            supplier_result = await db.execute(
                select(Supplier).where(
                    Supplier.id == request.supplier_id,
                    Supplier.tenant_id == current_user.tenant_id,
                )
            )
            supplier = supplier_result.scalar_one_or_none()
            if not supplier:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Supplier not found",
                )

            # Generate order number
            order_number = f"PO-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

            # Create purchase order
            po = PurchaseOrder(
                tenant_id=current_user.tenant_id,
                order_number=order_number,
                supplier_id=request.supplier_id,
                order_date=request.order_date,
                expected_delivery=request.expected_delivery,
                notes=request.notes,
                created_by=current_user.id,
            )
            db.add(po)
            await db.flush()

            # Create order items
            total_amount = Decimal("0")
            for item_data in request.items:
                item = PurchaseOrderItem(
                    tenant_id=current_user.tenant_id,
                    purchase_order_id=po.id,
                    product_id=item_data["product_id"],
                    quantity=Decimal(str(item_data["quantity"])),
                    unit_cost=Decimal(str(item_data["unit_cost"])),
                    total_cost=Decimal(str(item_data["quantity"]))
                    * Decimal(str(item_data["unit_cost"])),
                )
                total_amount += item.total_cost
                db.add(item)

            po.total_amount = total_amount
            await db.commit()

            logger.info(
                "purchase_order_created",
                po_id=po.id,
                order_number=order_number,
                supplier_id=request.supplier_id,
            )

            return {
                "id": po.id,
                "order_number": order_number,
                "total_amount": float(total_amount),
            }

        # ============================================================================
        # Inventory Count Endpoints
        # ============================================================================

        @router.post("/count/start", status_code=status.HTTP_201_CREATED)
        async def start_inventory_count(
            request: InventoryCountCreate,
            current_user: User = Depends(get_current_user),
            db: AsyncSession = Depends(get_db),
        ):
            """Start a new inventory count session."""
            count_number = f"IC-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

            count = InventoryCount(
                tenant_id=current_user.tenant_id,
                count_number=count_number,
                start_time=datetime.utcnow(),
                notes=request.notes,
                created_by=current_user.id,
            )
            db.add(count)
            await db.commit()
            await db.refresh(count)

            logger.info(
                "inventory_count_started", count_id=count.id, count_number=count_number
            )

            return {
                "id": count.id,
                "count_number": count_number,
                "start_time": count.start_time,
            }

        @router.post("/count/submit")
        async def submit_inventory_count(
            count_id: int,
            request: InventoryCountSubmit,
            current_user: User = Depends(get_current_user),
            db: AsyncSession = Depends(get_db),
        ):
            """Submit count results and adjust stock."""
            # Get count
            result = await db.execute(
                select(InventoryCount).where(
                    InventoryCount.id == count_id,
                    InventoryCount.tenant_id == current_user.tenant_id,
                )
            )
            count = result.scalar_one_or_none()
            if not count:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Inventory count not found",
                )

            # Process each counted item
            for item_data in request.items:
                product_id = item_data["product_id"]
                counted_quantity = Decimal(str(item_data["counted_quantity"]))

                # Get current stock
                stock_result = await db.execute(
                    select(StockLevel).where(
                        StockLevel.tenant_id == current_user.tenant_id,
                        StockLevel.product_id == product_id,
                    )
                )
                stock = stock_result.scalar_one_or_none()

                expected_quantity = stock.quantity if stock else Decimal("0")
                difference = counted_quantity - expected_quantity

                # Create count item
                count_item = InventoryCountItem(
                    tenant_id=current_user.tenant_id,
                    count_id=count_id,
                    product_id=product_id,
                    expected_quantity=expected_quantity,
                    counted_quantity=counted_quantity,
                    difference=difference,
                    notes=item_data.get("notes"),
                )
                db.add(count_item)

                # Adjust stock if difference
                if difference != 0:
                    if not stock:
                        stock = StockLevel(
                            tenant_id=current_user.tenant_id,
                            product_id=product_id,
                            quantity=counted_quantity,
                        )
                        db.add(stock)
                    else:
                        stock.quantity = counted_quantity

                    # Create movement record
                    movement = StockMovement(
                        tenant_id=current_user.tenant_id,
                        product_id=product_id,
                        movement_type="adjustment",
                        quantity=abs(difference),
                        quantity_before=expected_quantity,
                        quantity_after=counted_quantity,
                        reference_type="inventory_count",
                        reference_id=count_id,
                        created_by=current_user.id,
                    )
                    db.add(movement)

            # Mark count as completed
            count.status = "completed"
            count.end_time = datetime.utcnow()
            await db.commit()

            logger.info("inventory_count_completed", count_id=count_id)

            return {"message": "Inventory count completed successfully"}

        return router


# ============================================================================
# Plugin Instance (for auto-discovery)
# ============================================================================

plugin = InventoryManagementPlugin()

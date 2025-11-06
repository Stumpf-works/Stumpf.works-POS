"""
Kitchen Display System Plugin

Features:
- Real-time order display
- Priority sorting by time
- Timer per dish
- Status changes (new → in progress → completed)
- Multi-station support (grill, cold, dessert, bar)
- Color coding by urgency
- Acoustic alarms
- Waiter notification when ready
- Statistics (throughput time, rush hours)
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, select
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


class KitchenStation(SQLBase, TenantMixin):
    """Kitchen workstations."""

    __tablename__ = "plugin_kitchen_stations"

    station_name = Column(String(100), nullable=False)
    station_type = Column(String(50), nullable=False)  # grill, cold, dessert, bar, etc.
    display_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    color = Column(String(20), nullable=True)  # For UI color coding


class KitchenOrder(SQLBase, TenantMixin):
    """Kitchen orders."""

    __tablename__ = "plugin_kitchen_orders"

    order_number = Column(String(50), nullable=False)
    table_number = Column(Integer, nullable=True)
    order_type = Column(String(20), default="dine_in")  # dine_in, takeout, delivery
    status = Column(String(20), default="new")  # new, in_progress, completed, cancelled
    priority = Column(Integer, default=0)  # 0=normal, 1=high, 2=urgent
    received_at = Column(DateTime, nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    prep_time_minutes = Column(Integer, nullable=True)
    actual_time_minutes = Column(Integer, nullable=True)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    notes = Column(String(1000), nullable=True)


class KitchenOrderItem(SQLBase, TenantMixin):
    """Individual items in kitchen orders."""

    __tablename__ = "plugin_kitchen_order_items"

    order_id = Column(Integer, ForeignKey("plugin_kitchen_orders.id"), nullable=False)
    station_id = Column(
        Integer, ForeignKey("plugin_kitchen_stations.id"), nullable=True
    )
    item_name = Column(String(200), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    status = Column(String(20), default="pending")  # pending, cooking, ready, served
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    prep_time_minutes = Column(Integer, nullable=True)
    special_instructions = Column(String(500), nullable=True)


class KitchenTimer(SQLBase, TenantMixin):
    """Timers for tracking cooking times."""

    __tablename__ = "plugin_kitchen_timers"

    order_id = Column(Integer, ForeignKey("plugin_kitchen_orders.id"), nullable=False)
    order_item_id = Column(
        Integer, ForeignKey("plugin_kitchen_order_items.id"), nullable=True
    )
    station_id = Column(
        Integer, ForeignKey("plugin_kitchen_stations.id"), nullable=True
    )
    timer_name = Column(String(100), nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    started_at = Column(DateTime, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    alerted = Column(Boolean, default=False)


class KitchenStats(SQLBase, TenantMixin):
    """Kitchen performance statistics."""

    __tablename__ = "plugin_kitchen_stats"

    stat_date = Column(DateTime, nullable=False)
    station_id = Column(
        Integer, ForeignKey("plugin_kitchen_stations.id"), nullable=True
    )
    total_orders = Column(Integer, default=0)
    completed_orders = Column(Integer, default=0)
    cancelled_orders = Column(Integer, default=0)
    average_prep_time = Column(Integer, nullable=True)
    peak_hour = Column(Integer, nullable=True)  # Hour of day (0-23)
    total_items = Column(Integer, default=0)


# ============================================================================
# API Models (Pydantic)
# ============================================================================


class KitchenStationCreate(BaseModel):
    """Request to create a station."""

    station_name: str
    station_type: str
    display_order: int = 0
    color: Optional[str] = None


class KitchenStationInfo(BaseModel):
    """Station information."""

    id: int
    station_name: str
    station_type: str
    display_order: int
    is_active: bool
    color: Optional[str]

    class Config:
        from_attributes = True


class KitchenOrderItemCreate(BaseModel):
    """Order item creation."""

    item_name: str
    quantity: int = 1
    station_id: Optional[int] = None
    prep_time_minutes: Optional[int] = None
    special_instructions: Optional[str] = None


class KitchenOrderCreate(BaseModel):
    """Request to create a kitchen order."""

    order_number: str
    table_number: Optional[int] = None
    order_type: str = "dine_in"
    priority: int = 0
    items: List[KitchenOrderItemCreate]
    notes: Optional[str] = None


class KitchenOrderItemInfo(BaseModel):
    """Order item information."""

    id: int
    item_name: str
    quantity: int
    status: str
    station_id: Optional[int]
    station_name: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    prep_time_minutes: Optional[int]
    special_instructions: Optional[str]

    class Config:
        from_attributes = True


class KitchenOrderInfo(BaseModel):
    """Kitchen order information."""

    id: int
    order_number: str
    table_number: Optional[int]
    order_type: str
    status: str
    priority: int
    received_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    prep_time_minutes: Optional[int]
    actual_time_minutes: Optional[int]
    notes: Optional[str]
    items: List[KitchenOrderItemInfo] = []
    elapsed_minutes: int = 0
    is_urgent: bool = False

    class Config:
        from_attributes = True


class KitchenOrderStatusUpdate(BaseModel):
    """Request to update order status."""

    status: str = Field(..., pattern="^(new|in_progress|completed|cancelled)$")


# ============================================================================
# Plugin Class
# ============================================================================


class KitchenDisplayPlugin(BasePlugin):
    """
    Kitchen Display System Plugin.

    Provides real-time kitchen order management and display.
    """

    def __init__(self):
        super().__init__()
        self.config = {
            "enable_timers": True,
            "default_prep_time_minutes": 15,
            "alert_after_minutes": 20,
            "stations": ["Grill", "Kalt", "Dessert", "Bar"],
            "auto_print_receipt": True,
        }

    def get_metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        return PluginMetadata(
            name="kitchen_display",
            version="1.0.0",
            description="Digital kitchen display system with real-time order tracking",
            author="Stumpf.works",
            dependencies=[],
        )

    def get_name(self) -> str:
        """Get plugin name."""
        return "kitchen_display"

    def get_display_name(self) -> str:
        """Get plugin display name."""
        return "Küchen-Display"

    def get_description(self) -> str:
        """Get plugin description."""
        return "Digitales Küchen-Display mit Echtzeit-Bestellverfolgung"

    def get_version(self) -> str:
        """Get plugin version."""
        return self.metadata.version

    def get_author(self) -> str:
        """Get plugin author."""
        return self.metadata.author

    def get_category(self) -> str:
        """Get plugin category."""
        return "restaurant"

    def get_requires(self) -> List[str]:
        """Get plugin dependencies."""
        return self.metadata.dependencies

    def get_config_schema(self) -> Optional[Dict]:
        """Get plugin configuration schema."""
        return {
            "type": "object",
            "properties": {
                "enable_timers": {
                    "type": "boolean",
                    "default": True,
                    "description": "Timer aktivieren",
                },
                "default_prep_time_minutes": {
                    "type": "integer",
                    "default": 15,
                    "minimum": 1,
                    "maximum": 240,
                    "description": "Standard-Zubereitungszeit (Minuten)",
                },
                "alert_after_minutes": {
                    "type": "integer",
                    "default": 20,
                    "minimum": 1,
                    "maximum": 240,
                    "description": "Alarm nach Minuten",
                },
                "stations": {
                    "type": "array",
                    "items": {"type": "string"},
                    "default": ["Grill", "Kalt", "Dessert", "Bar"],
                    "description": "Küchenstationen",
                },
                "auto_print_receipt": {
                    "type": "boolean",
                    "default": True,
                    "description": "Bon automatisch drucken",
                },
            },
        }

    def configure(self, config: Dict):
        """Configure plugin with settings."""
        prep_time = config.get("default_prep_time_minutes", 15)
        if prep_time < 1 or prep_time > 240:
            raise ValueError("default_prep_time_minutes must be between 1 and 240")

        self.config.update(config)
        logger.info("kitchen_display_configured", config=self.config)

    def get_models(self) -> List[Any]:
        """Return database models."""
        return [
            KitchenStation,
            KitchenOrder,
            KitchenOrderItem,
            KitchenTimer,
            KitchenStats,
        ]

    async def on_enable(self):
        """Called when plugin is enabled."""
        logger.info("kitchen_display_enabled")

    async def on_disable(self):
        """Called when plugin is disabled."""
        logger.info("kitchen_display_disabled")

    def get_router(self) -> APIRouter:
        """Return API router with endpoints."""
        router = APIRouter(prefix="/kitchen", tags=["Restaurant - Kitchen Display"])

        # ============================================================================
        # Station Endpoints
        # ============================================================================

        @router.get("/stations", response_model=List[KitchenStationInfo])
        async def list_stations(
            current_user: User = Depends(get_current_user),
            db: AsyncSession = Depends(get_db),
        ):
            """List all kitchen stations."""
            result = await db.execute(
                select(KitchenStation)
                .where(
                    KitchenStation.tenant_id == current_user.tenant_id,
                    KitchenStation.is_active == True,  # noqa
                )
                .order_by(KitchenStation.display_order)
            )
            stations = result.scalars().all()

            return [
                KitchenStationInfo(
                    id=s.id,
                    station_name=s.station_name,
                    station_type=s.station_type,
                    display_order=s.display_order,
                    is_active=s.is_active,
                    color=s.color,
                )
                for s in stations
            ]

        @router.post("/stations", status_code=status.HTTP_201_CREATED)
        async def create_station(
            request: KitchenStationCreate,
            current_user: User = Depends(get_current_user),
            db: AsyncSession = Depends(get_db),
        ):
            """Create a new kitchen station."""
            station = KitchenStation(
                tenant_id=current_user.tenant_id,
                station_name=request.station_name,
                station_type=request.station_type,
                display_order=request.display_order,
                color=request.color,
            )
            db.add(station)
            await db.commit()
            await db.refresh(station)

            logger.info(
                "kitchen_station_created",
                station_id=station.id,
                name=request.station_name,
            )

            return {"id": station.id, "station_name": request.station_name}

        # ============================================================================
        # Order Endpoints
        # ============================================================================

        @router.get("/orders/active", response_model=List[KitchenOrderInfo])
        async def get_active_orders(
            station_id: Optional[int] = Query(None),
            current_user: User = Depends(get_current_user),
            db: AsyncSession = Depends(get_db),
        ):
            """Get all active kitchen orders."""
            query = select(KitchenOrder).where(
                KitchenOrder.tenant_id == current_user.tenant_id,
                KitchenOrder.status.in_(["new", "in_progress"]),
            )

            query = query.order_by(KitchenOrder.received_at)

            result = await db.execute(query)
            orders = result.scalars().all()

            orders_info = []
            for order in orders:
                # Get order items
                items_result = await db.execute(
                    select(KitchenOrderItem).where(
                        KitchenOrderItem.order_id == order.id
                    )
                )
                items = items_result.scalars().all()

                # Filter by station if specified
                if station_id:
                    items = [i for i in items if i.station_id == station_id]
                    if not items:
                        continue

                # Get item info with station names
                items_info = []
                for item in items:
                    station_name = None
                    if item.station_id:
                        station_result = await db.execute(
                            select(KitchenStation).where(
                                KitchenStation.id == item.station_id
                            )
                        )
                        station = station_result.scalar_one_or_none()
                        if station:
                            station_name = station.station_name

                    items_info.append(
                        KitchenOrderItemInfo(
                            id=item.id,
                            item_name=item.item_name,
                            quantity=item.quantity,
                            status=item.status,
                            station_id=item.station_id,
                            station_name=station_name,
                            started_at=item.started_at,
                            completed_at=item.completed_at,
                            prep_time_minutes=item.prep_time_minutes,
                            special_instructions=item.special_instructions,
                        )
                    )

                # Calculate elapsed time
                elapsed = datetime.utcnow() - order.received_at
                elapsed_minutes = int(elapsed.total_seconds() / 60)

                # Check if urgent
                alert_threshold = self.config["alert_after_minutes"]
                is_urgent = elapsed_minutes >= alert_threshold or order.priority > 0

                orders_info.append(
                    KitchenOrderInfo(
                        id=order.id,
                        order_number=order.order_number,
                        table_number=order.table_number,
                        order_type=order.order_type,
                        status=order.status,
                        priority=order.priority,
                        received_at=order.received_at,
                        started_at=order.started_at,
                        completed_at=order.completed_at,
                        prep_time_minutes=order.prep_time_minutes,
                        actual_time_minutes=order.actual_time_minutes,
                        notes=order.notes,
                        items=items_info,
                        elapsed_minutes=elapsed_minutes,
                        is_urgent=is_urgent,
                    )
                )

            return orders_info

        @router.post("/orders", status_code=status.HTTP_201_CREATED)
        async def create_order(
            request: KitchenOrderCreate,
            current_user: User = Depends(get_current_user),
            db: AsyncSession = Depends(get_db),
        ):
            """Create a new kitchen order."""
            # Create order
            order = KitchenOrder(
                tenant_id=current_user.tenant_id,
                order_number=request.order_number,
                table_number=request.table_number,
                order_type=request.order_type,
                priority=request.priority,
                received_at=datetime.utcnow(),
                notes=request.notes,
            )
            db.add(order)
            await db.flush()

            # Create order items
            for item_data in request.items:
                item = KitchenOrderItem(
                    tenant_id=current_user.tenant_id,
                    order_id=order.id,
                    station_id=item_data.station_id,
                    item_name=item_data.item_name,
                    quantity=item_data.quantity,
                    prep_time_minutes=item_data.prep_time_minutes
                    or self.config["default_prep_time_minutes"],
                    special_instructions=item_data.special_instructions,
                )
                db.add(item)

            await db.commit()
            await db.refresh(order)

            logger.info(
                "kitchen_order_created",
                order_id=order.id,
                order_number=request.order_number,
            )

            return {
                "id": order.id,
                "order_number": request.order_number,
                "received_at": order.received_at,
            }

        @router.patch("/orders/{order_id}/status")
        async def update_order_status(
            order_id: int,
            request: KitchenOrderStatusUpdate,
            current_user: User = Depends(get_current_user),
            db: AsyncSession = Depends(get_db),
        ):
            """Update order status."""
            # Get order
            result = await db.execute(
                select(KitchenOrder).where(
                    KitchenOrder.id == order_id,
                    KitchenOrder.tenant_id == current_user.tenant_id,
                )
            )
            order = result.scalar_one_or_none()

            if not order:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Order not found",
                )

            # Update status
            old_status = order.status
            order.status = request.status

            # Update timestamps
            if request.status == "in_progress" and not order.started_at:
                order.started_at = datetime.utcnow()

            if request.status == "completed" and not order.completed_at:
                order.completed_at = datetime.utcnow()

                # Calculate actual time
                if order.started_at:
                    duration = order.completed_at - order.started_at
                    order.actual_time_minutes = int(duration.total_seconds() / 60)

            await db.commit()

            logger.info(
                "kitchen_order_status_updated",
                order_id=order_id,
                old_status=old_status,
                new_status=request.status,
            )

            return {
                "order_id": order_id,
                "status": request.status,
                "message": f"Order status updated to {request.status}",
            }

        @router.post("/orders/{order_id}/start")
        async def start_order(
            order_id: int,
            current_user: User = Depends(get_current_user),
            db: AsyncSession = Depends(get_db),
        ):
            """Start cooking an order (activate timer)."""
            # Get order
            result = await db.execute(
                select(KitchenOrder).where(
                    KitchenOrder.id == order_id,
                    KitchenOrder.tenant_id == current_user.tenant_id,
                )
            )
            order = result.scalar_one_or_none()

            if not order:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Order not found",
                )

            # Update order status
            order.status = "in_progress"
            order.started_at = datetime.utcnow()

            # Create timer if enabled
            if self.config["enable_timers"]:
                prep_time = (
                    order.prep_time_minutes or self.config["default_prep_time_minutes"]
                )
                timer = KitchenTimer(
                    tenant_id=current_user.tenant_id,
                    order_id=order.id,
                    timer_name=f"Order {order.order_number}",
                    duration_minutes=prep_time,
                    started_at=datetime.utcnow(),
                    expires_at=datetime.utcnow() + timedelta(minutes=prep_time),
                )
                db.add(timer)

            # Update all items to cooking
            items_result = await db.execute(
                select(KitchenOrderItem).where(KitchenOrderItem.order_id == order_id)
            )
            items = items_result.scalars().all()

            for item in items:
                item.status = "cooking"
                item.started_at = datetime.utcnow()

            await db.commit()

            logger.info("kitchen_order_started", order_id=order_id)

            return {
                "order_id": order_id,
                "started_at": order.started_at,
                "message": "Order started",
            }

        @router.post("/orders/{order_id}/complete")
        async def complete_order(
            order_id: int,
            current_user: User = Depends(get_current_user),
            db: AsyncSession = Depends(get_db),
        ):
            """Mark order as completed."""
            # Get order
            result = await db.execute(
                select(KitchenOrder).where(
                    KitchenOrder.id == order_id,
                    KitchenOrder.tenant_id == current_user.tenant_id,
                )
            )
            order = result.scalar_one_or_none()

            if not order:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Order not found",
                )

            # Update order
            order.status = "completed"
            order.completed_at = datetime.utcnow()

            # Calculate actual time
            if order.started_at:
                duration = order.completed_at - order.started_at
                order.actual_time_minutes = int(duration.total_seconds() / 60)
            else:
                duration = order.completed_at - order.received_at
                order.actual_time_minutes = int(duration.total_seconds() / 60)

            # Mark all items as ready
            items_result = await db.execute(
                select(KitchenOrderItem).where(KitchenOrderItem.order_id == order_id)
            )
            items = items_result.scalars().all()

            for item in items:
                item.status = "ready"
                item.completed_at = datetime.utcnow()

            # Deactivate timers
            timers_result = await db.execute(
                select(KitchenTimer).where(
                    KitchenTimer.order_id == order_id,
                    KitchenTimer.is_active == True,  # noqa
                )
            )
            timers = timers_result.scalars().all()

            for timer in timers:
                timer.is_active = False

            await db.commit()

            logger.info(
                "kitchen_order_completed",
                order_id=order_id,
                actual_time=order.actual_time_minutes,
            )

            return {
                "order_id": order_id,
                "completed_at": order.completed_at,
                "actual_time_minutes": order.actual_time_minutes,
                "message": "Order completed",
            }

        # ============================================================================
        # Statistics Endpoints
        # ============================================================================

        @router.get("/stats")
        async def get_statistics(
            date: Optional[datetime] = Query(None),
            current_user: User = Depends(get_current_user),
            db: AsyncSession = Depends(get_db),
        ):
            """Get kitchen statistics."""
            target_date = date or datetime.utcnow()
            start_of_day = target_date.replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            end_of_day = start_of_day + timedelta(days=1)

            # Get orders for the day
            result = await db.execute(
                select(KitchenOrder).where(
                    KitchenOrder.tenant_id == current_user.tenant_id,
                    KitchenOrder.received_at >= start_of_day,
                    KitchenOrder.received_at < end_of_day,
                )
            )
            orders = result.scalars().all()

            total_orders = len(orders)
            completed_orders = sum(1 for o in orders if o.status == "completed")
            cancelled_orders = sum(1 for o in orders if o.status == "cancelled")
            in_progress = sum(1 for o in orders if o.status in ["new", "in_progress"])

            # Calculate average prep time
            prep_times = [
                o.actual_time_minutes for o in orders if o.actual_time_minutes
            ]
            avg_prep_time = int(sum(prep_times) / len(prep_times)) if prep_times else 0

            # Find peak hour
            hour_counts = {}
            for order in orders:
                hour = order.received_at.hour
                hour_counts[hour] = hour_counts.get(hour, 0) + 1

            peak_hour = (
                max(hour_counts.items(), key=lambda x: x[1])[0] if hour_counts else None
            )

            return {
                "date": target_date.date().isoformat(),
                "total_orders": total_orders,
                "completed_orders": completed_orders,
                "cancelled_orders": cancelled_orders,
                "in_progress": in_progress,
                "average_prep_time_minutes": avg_prep_time,
                "peak_hour": peak_hour,
            }

        return router


# ============================================================================
# Plugin Instance (for auto-discovery)
# ============================================================================

plugin = KitchenDisplayPlugin()

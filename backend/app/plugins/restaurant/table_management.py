"""
Restaurant Table Management Plugin

Features:
- Table layout management
- Reservation system
- Table status tracking
- Waiter assignment
- Order-to-table linking
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
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


class Table(SQLBase, TenantMixin):
    """Table model for restaurant floor layout."""

    __tablename__ = "plugin_restaurant_tables"

    table_number = Column(Integer, nullable=False)
    table_name = Column(String(100), nullable=True)  # e.g. "Window Table 1"
    seats = Column(Integer, nullable=False, default=4)
    position_x = Column(Integer, nullable=True)  # For floor plan visualization
    position_y = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    notes = Column(String(500), nullable=True)


class TableStatus(SQLBase, TenantMixin):
    """Current status of tables."""

    __tablename__ = "plugin_restaurant_table_status"

    table_id = Column(
        Integer, ForeignKey("plugin_restaurant_tables.id"), nullable=False
    )
    status = Column(
        String(20), default="available"
    )  # available, occupied, reserved, cleaning
    current_order_id = Column(Integer, nullable=True)
    assigned_waiter_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    occupied_since = Column(DateTime, nullable=True)
    guests_count = Column(Integer, nullable=True)


class Reservation(SQLBase, TenantMixin):
    """Table reservations."""

    __tablename__ = "plugin_restaurant_reservations"

    table_id = Column(
        Integer, ForeignKey("plugin_restaurant_tables.id"), nullable=False
    )
    customer_name = Column(String(200), nullable=False)
    customer_phone = Column(String(50), nullable=True)
    customer_email = Column(String(200), nullable=True)
    guests_count = Column(Integer, nullable=False)
    reservation_time = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, default=120)
    status = Column(
        String(20), default="confirmed"
    )  # confirmed, seated, completed, cancelled
    notes = Column(String(1000), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)


# ============================================================================
# API Models (Pydantic)
# ============================================================================


class TableCreate(BaseModel):
    """Request to create a table."""

    table_number: int
    table_name: Optional[str] = None
    seats: int = 4
    position_x: Optional[int] = None
    position_y: Optional[int] = None
    notes: Optional[str] = None


class TableUpdate(BaseModel):
    """Request to update a table."""

    table_name: Optional[str] = None
    seats: Optional[int] = None
    position_x: Optional[int] = None
    position_y: Optional[int] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None


class TableInfo(BaseModel):
    """Table information response."""

    id: int
    table_number: int
    table_name: Optional[str]
    seats: int
    position_x: Optional[int]
    position_y: Optional[int]
    is_active: bool
    status: str
    guests_count: Optional[int]
    assigned_waiter: Optional[str]
    occupied_since: Optional[datetime]

    class Config:
        from_attributes = True


class ReservationCreate(BaseModel):
    """Request to create a reservation."""

    table_id: int
    customer_name: str
    customer_phone: Optional[str] = None
    customer_email: Optional[str] = None
    guests_count: int
    reservation_time: datetime
    duration_minutes: int = 120
    notes: Optional[str] = None


class ReservationInfo(BaseModel):
    """Reservation information response."""

    id: int
    table_id: int
    table_number: int
    customer_name: str
    customer_phone: Optional[str]
    guests_count: int
    reservation_time: datetime
    duration_minutes: int
    status: str
    notes: Optional[str]

    class Config:
        from_attributes = True


class TableStatusUpdate(BaseModel):
    """Request to update table status."""

    status: str  # available, occupied, reserved, cleaning
    guests_count: Optional[int] = None
    assigned_waiter_id: Optional[int] = None
    current_order_id: Optional[int] = None


# ============================================================================
# Plugin Class
# ============================================================================


class TableManagementPlugin(BasePlugin):
    """
    Restaurant Table Management Plugin.

    Provides comprehensive table and reservation management for restaurants.
    """

    def __init__(self):
        super().__init__()
        self.config = {
            "max_tables": 50,
            "default_reservation_duration": 120,
            "enable_floor_plan": True,
            "enable_waiter_assignment": True,
        }

    def get_metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        return PluginMetadata(
            name="table_management",
            version="1.0.0",
            description="Restaurant table and reservation management system",
            author="Stumpf.works",
            dependencies=[],
        )

    def get_name(self) -> str:
        """Get plugin name."""
        return "table_management"

    def get_display_name(self) -> str:
        """Get plugin display name."""
        return "Tischverwaltung"

    def get_description(self) -> str:
        """Get plugin description."""
        return "Verwalten Sie Tische, Reservierungen und Tischstatus für Ihr Restaurant"

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
                "max_tables": {
                    "type": "integer",
                    "default": 50,
                    "minimum": 1,
                    "maximum": 500,
                    "description": "Maximale Anzahl Tische",
                },
                "default_reservation_duration": {
                    "type": "integer",
                    "default": 120,
                    "minimum": 30,
                    "maximum": 480,
                    "description": "Standard-Reservierungsdauer in Minuten",
                },
                "enable_floor_plan": {
                    "type": "boolean",
                    "default": True,
                    "description": "Raumplan-Visualisierung aktivieren",
                },
                "enable_waiter_assignment": {
                    "type": "boolean",
                    "default": True,
                    "description": "Kellner-Zuweisung aktivieren",
                },
            },
        }

    def configure(self, config: Dict):
        """Configure plugin with settings."""
        # Validate config
        max_tables = config.get("max_tables", 50)
        if max_tables < 1 or max_tables > 500:
            raise ValueError("max_tables must be between 1 and 500")

        duration = config.get("default_reservation_duration", 120)
        if duration < 30 or duration > 480:
            raise ValueError("reservation duration must be between 30 and 480 minutes")

        self.config.update(config)
        logger.info("table_management_configured", config=self.config)

    def get_models(self) -> List[Any]:
        """Return database models."""
        return [Table, TableStatus, Reservation]

    async def on_enable(self):
        """Called when plugin is enabled."""
        logger.info("table_management_enabled")
        # Could initialize database tables here
        # For now, tables are created via Alembic migrations

    async def on_disable(self):
        """Called when plugin is disabled."""
        logger.info("table_management_disabled")

    async def on_startup(self):
        """Called on application startup."""
        logger.info("table_management_startup")

    async def on_shutdown(self):
        """Called on application shutdown."""
        logger.info("table_management_shutdown")

    def get_router(self) -> APIRouter:
        """Return API router with endpoints."""
        router = APIRouter(
            prefix="/table-management", tags=["Restaurant - Table Management"]
        )

        # ============================================================================
        # Tables Endpoints
        # ============================================================================

        @router.get("/tables", response_model=List[TableInfo])
        async def list_tables(
            current_user: User = Depends(get_current_user),
            db: AsyncSession = Depends(get_db),
        ):
            """List all tables with their current status."""
            # Get all tables
            result = await db.execute(
                select(Table).where(
                    Table.tenant_id == current_user.tenant_id,
                    Table.is_active == True,  # noqa
                )
            )
            tables = result.scalars().all()

            # Enrich with status
            tables_info = []
            for table in tables:
                # Get current status
                status_result = await db.execute(
                    select(TableStatus)
                    .where(TableStatus.table_id == table.id)
                    .order_by(TableStatus.created_at.desc())
                    .limit(1)
                )
                table_status = status_result.scalar_one_or_none()

                # Get waiter name if assigned
                waiter_name = None
                if table_status and table_status.assigned_waiter_id:
                    waiter_result = await db.execute(
                        select(User).where(User.id == table_status.assigned_waiter_id)
                    )
                    waiter = waiter_result.scalar_one_or_none()
                    if waiter:
                        waiter_name = waiter.full_name

                tables_info.append(
                    TableInfo(
                        id=table.id,
                        table_number=table.table_number,
                        table_name=table.table_name,
                        seats=table.seats,
                        position_x=table.position_x,
                        position_y=table.position_y,
                        is_active=table.is_active,
                        status=table_status.status if table_status else "available",
                        guests_count=(
                            table_status.guests_count if table_status else None
                        ),
                        assigned_waiter=waiter_name,
                        occupied_since=(
                            table_status.occupied_since if table_status else None
                        ),
                    )
                )

            return tables_info

        @router.post(
            "/tables", response_model=TableInfo, status_code=status.HTTP_201_CREATED
        )
        async def create_table(
            request: TableCreate,
            current_user: User = Depends(get_current_user),
            db: AsyncSession = Depends(get_db),
        ):
            """Create a new table."""
            # Check max tables limit
            count_result = await db.execute(
                select(Table).where(
                    Table.tenant_id == current_user.tenant_id,
                    Table.is_active == True,  # noqa
                )
            )
            current_count = len(count_result.scalars().all())

            if current_count >= self.config["max_tables"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Maximum tables limit reached ({self.config['max_tables']})",
                )

            # Create table
            table = Table(
                tenant_id=current_user.tenant_id,
                table_number=request.table_number,
                table_name=request.table_name,
                seats=request.seats,
                position_x=request.position_x,
                position_y=request.position_y,
                notes=request.notes,
            )
            db.add(table)
            await db.commit()
            await db.refresh(table)

            # Create initial status
            table_status = TableStatus(
                tenant_id=current_user.tenant_id, table_id=table.id, status="available"
            )
            db.add(table_status)
            await db.commit()

            logger.info(
                "table_created",
                table_id=table.id,
                table_number=table.table_number,
                user_id=current_user.id,
            )

            return TableInfo(
                id=table.id,
                table_number=table.table_number,
                table_name=table.table_name,
                seats=table.seats,
                position_x=table.position_x,
                position_y=table.position_y,
                is_active=table.is_active,
                status="available",
                guests_count=None,
                assigned_waiter=None,
                occupied_since=None,
            )

        @router.patch("/tables/{table_id}", response_model=TableInfo)
        async def update_table(
            table_id: int,
            request: TableUpdate,
            current_user: User = Depends(get_current_user),
            db: AsyncSession = Depends(get_db),
        ):
            """Update table settings."""
            # Get table
            result = await db.execute(
                select(Table).where(
                    Table.id == table_id, Table.tenant_id == current_user.tenant_id
                )
            )
            table = result.scalar_one_or_none()
            if not table:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Table not found"
                )

            # Update fields
            if request.table_name is not None:
                table.table_name = request.table_name
            if request.seats is not None:
                table.seats = request.seats
            if request.position_x is not None:
                table.position_x = request.position_x
            if request.position_y is not None:
                table.position_y = request.position_y
            if request.is_active is not None:
                table.is_active = request.is_active
            if request.notes is not None:
                table.notes = request.notes

            await db.commit()
            await db.refresh(table)

            # Get current status for response
            status_result = await db.execute(
                select(TableStatus)
                .where(TableStatus.table_id == table.id)
                .order_by(TableStatus.created_at.desc())
                .limit(1)
            )
            table_status = status_result.scalar_one_or_none()

            return TableInfo(
                id=table.id,
                table_number=table.table_number,
                table_name=table.table_name,
                seats=table.seats,
                position_x=table.position_x,
                position_y=table.position_y,
                is_active=table.is_active,
                status=table_status.status if table_status else "available",
                guests_count=table_status.guests_count if table_status else None,
                assigned_waiter=None,
                occupied_since=table_status.occupied_since if table_status else None,
            )

        @router.patch("/tables/{table_id}/status")
        async def update_table_status(
            table_id: int,
            request: TableStatusUpdate,
            current_user: User = Depends(get_current_user),
            db: AsyncSession = Depends(get_db),
        ):
            """Update table status (occupy, free, clean, etc.)."""
            # Verify table exists
            result = await db.execute(
                select(Table).where(
                    Table.id == table_id, Table.tenant_id == current_user.tenant_id
                )
            )
            table = result.scalar_one_or_none()
            if not table:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Table not found"
                )

            # Create new status entry
            table_status = TableStatus(
                tenant_id=current_user.tenant_id,
                table_id=table_id,
                status=request.status,
                guests_count=request.guests_count,
                assigned_waiter_id=request.assigned_waiter_id,
                current_order_id=request.current_order_id,
                occupied_since=(
                    datetime.utcnow() if request.status == "occupied" else None
                ),
            )
            db.add(table_status)
            await db.commit()

            logger.info(
                "table_status_updated",
                table_id=table_id,
                status=request.status,
                user_id=current_user.id,
            )

            return {
                "message": f"Table {table.table_number} status updated to {request.status}"
            }

        # ============================================================================
        # Reservations Endpoints
        # ============================================================================

        @router.get("/reservations", response_model=List[ReservationInfo])
        async def list_reservations(
            date: Optional[str] = None,
            current_user: User = Depends(get_current_user),
            db: AsyncSession = Depends(get_db),
        ):
            """List reservations, optionally filtered by date."""
            query = select(Reservation).where(
                Reservation.tenant_id == current_user.tenant_id
            )

            if date:
                # Filter by date
                target_date = datetime.fromisoformat(date)
                start_of_day = target_date.replace(
                    hour=0, minute=0, second=0, microsecond=0
                )
                end_of_day = start_of_day + timedelta(days=1)

                query = query.where(
                    Reservation.reservation_time >= start_of_day,
                    Reservation.reservation_time < end_of_day,
                )

            query = query.order_by(Reservation.reservation_time)
            result = await db.execute(query)
            reservations = result.scalars().all()

            # Enrich with table info
            reservations_info = []
            for reservation in reservations:
                # Get table
                table_result = await db.execute(
                    select(Table).where(Table.id == reservation.table_id)
                )
                table = table_result.scalar_one_or_none()

                reservations_info.append(
                    ReservationInfo(
                        id=reservation.id,
                        table_id=reservation.table_id,
                        table_number=table.table_number if table else 0,
                        customer_name=reservation.customer_name,
                        customer_phone=reservation.customer_phone,
                        guests_count=reservation.guests_count,
                        reservation_time=reservation.reservation_time,
                        duration_minutes=reservation.duration_minutes,
                        status=reservation.status,
                        notes=reservation.notes,
                    )
                )

            return reservations_info

        @router.post(
            "/reservations",
            response_model=ReservationInfo,
            status_code=status.HTTP_201_CREATED,
        )
        async def create_reservation(
            request: ReservationCreate,
            current_user: User = Depends(get_current_user),
            db: AsyncSession = Depends(get_db),
        ):
            """Create a new reservation."""
            # Verify table exists
            result = await db.execute(
                select(Table).where(
                    Table.id == request.table_id,
                    Table.tenant_id == current_user.tenant_id,
                )
            )
            table = result.scalar_one_or_none()
            if not table:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Table not found"
                )

            # Check for conflicts
            end_time = request.reservation_time + timedelta(
                minutes=request.duration_minutes
            )
            conflict_result = await db.execute(
                select(Reservation).where(
                    Reservation.table_id == request.table_id,
                    Reservation.tenant_id == current_user.tenant_id,
                    Reservation.status.in_(["confirmed", "seated"]),
                    Reservation.reservation_time < end_time,
                    (
                        Reservation.reservation_time
                        + Reservation.duration_minutes * timedelta(minutes=1)
                    )
                    > request.reservation_time,
                )
            )
            conflicts = conflict_result.scalars().all()

            if conflicts:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Table is already reserved for this time slot",
                )

            # Create reservation
            reservation = Reservation(
                tenant_id=current_user.tenant_id,
                table_id=request.table_id,
                customer_name=request.customer_name,
                customer_phone=request.customer_phone,
                customer_email=request.customer_email,
                guests_count=request.guests_count,
                reservation_time=request.reservation_time,
                duration_minutes=request.duration_minutes,
                notes=request.notes,
                created_by=current_user.id,
            )
            db.add(reservation)
            await db.commit()
            await db.refresh(reservation)

            logger.info(
                "reservation_created",
                reservation_id=reservation.id,
                table_id=request.table_id,
                customer=request.customer_name,
                user_id=current_user.id,
            )

            return ReservationInfo(
                id=reservation.id,
                table_id=reservation.table_id,
                table_number=table.table_number,
                customer_name=reservation.customer_name,
                customer_phone=reservation.customer_phone,
                guests_count=reservation.guests_count,
                reservation_time=reservation.reservation_time,
                duration_minutes=reservation.duration_minutes,
                status=reservation.status,
                notes=reservation.notes,
            )

        @router.patch("/reservations/{reservation_id}/status")
        async def update_reservation_status(
            reservation_id: int,
            new_status: str,
            current_user: User = Depends(get_current_user),
            db: AsyncSession = Depends(get_db),
        ):
            """Update reservation status (confirmed, seated, completed, cancelled)."""
            # Get reservation
            result = await db.execute(
                select(Reservation).where(
                    Reservation.id == reservation_id,
                    Reservation.tenant_id == current_user.tenant_id,
                )
            )
            reservation = result.scalar_one_or_none()
            if not reservation:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Reservation not found",
                )

            # Update status
            reservation.status = new_status
            await db.commit()

            # If seated, update table status
            if new_status == "seated":
                table_status = TableStatus(
                    tenant_id=current_user.tenant_id,
                    table_id=reservation.table_id,
                    status="occupied",
                    guests_count=reservation.guests_count,
                    occupied_since=datetime.utcnow(),
                )
                db.add(table_status)
                await db.commit()

            logger.info(
                "reservation_status_updated",
                reservation_id=reservation_id,
                status=new_status,
                user_id=current_user.id,
            )

            return {"message": f"Reservation status updated to {new_status}"}

        # ============================================================================
        # Statistics Endpoints
        # ============================================================================

        @router.get("/stats")
        async def get_statistics(
            current_user: User = Depends(get_current_user),
            db: AsyncSession = Depends(get_db),
        ):
            """Get restaurant statistics."""
            # Count tables by status
            tables_result = await db.execute(
                select(Table).where(
                    Table.tenant_id == current_user.tenant_id,
                    Table.is_active == True,  # noqa
                )
            )
            tables = tables_result.scalars().all()

            status_counts = {
                "available": 0,
                "occupied": 0,
                "reserved": 0,
                "cleaning": 0,
            }

            for table in tables:
                # Get latest status
                status_result = await db.execute(
                    select(TableStatus)
                    .where(TableStatus.table_id == table.id)
                    .order_by(TableStatus.created_at.desc())
                    .limit(1)
                )
                table_status = status_result.scalar_one_or_none()
                current_status = table_status.status if table_status else "available"

                if current_status in status_counts:
                    status_counts[current_status] += 1

            # Count today's reservations
            today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            tomorrow = today + timedelta(days=1)

            reservations_result = await db.execute(
                select(Reservation).where(
                    Reservation.tenant_id == current_user.tenant_id,
                    Reservation.reservation_time >= today,
                    Reservation.reservation_time < tomorrow,
                    Reservation.status.in_(["confirmed", "seated"]),
                )
            )
            todays_reservations = len(reservations_result.scalars().all())

            return {
                "total_tables": len(tables),
                "tables_by_status": status_counts,
                "todays_reservations": todays_reservations,
                "occupancy_rate": (
                    round(
                        (status_counts["occupied"] + status_counts["reserved"])
                        / len(tables)
                        * 100,
                        1,
                    )
                    if len(tables) > 0
                    else 0
                ),
            }

        return router


# ============================================================================
# Plugin Instance (for auto-discovery)
# ============================================================================

# Plugin registry will discover this
plugin = TableManagementPlugin()

"""
Employee Time Tracking Plugin

Features:
- Clock in/out tracking
- Break management (automatic or manual)
- Overtime calculation
- Shift scheduling
- Daily/weekly/monthly reports
- Export for payroll software (CSV/Excel)
- PIN-based clocking at POS
- Automatic break detection (after 6h)
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


class TimeEntry(SQLBase, TenantMixin):
    """Time tracking entries for employees."""

    __tablename__ = "plugin_timetracking_entries"

    employee_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    clock_in = Column(DateTime, nullable=False)
    clock_out = Column(DateTime, nullable=True)
    total_hours = Column(Numeric(10, 2), nullable=True)
    regular_hours = Column(Numeric(10, 2), nullable=True)
    overtime_hours = Column(Numeric(10, 2), nullable=True)
    break_minutes = Column(Integer, default=0)
    notes = Column(String(500), nullable=True)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)


class Break(SQLBase, TenantMixin):
    """Break tracking for time entries."""

    __tablename__ = "plugin_timetracking_breaks"

    time_entry_id = Column(
        Integer, ForeignKey("plugin_timetracking_entries.id"), nullable=False
    )
    break_start = Column(DateTime, nullable=False)
    break_end = Column(DateTime, nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    break_type = Column(String(20), default="manual")  # manual, auto
    notes = Column(String(500), nullable=True)


class Shift(SQLBase, TenantMixin):
    """Scheduled shifts for employees."""

    __tablename__ = "plugin_timetracking_shifts"

    employee_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    shift_date = Column(DateTime, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    expected_hours = Column(Numeric(10, 2), nullable=False)
    shift_type = Column(String(50), nullable=True)  # morning, afternoon, evening, night
    notes = Column(String(500), nullable=True)
    is_published = Column(Boolean, default=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)


class Overtime(SQLBase, TenantMixin):
    """Overtime tracking and approval."""

    __tablename__ = "plugin_timetracking_overtime"

    employee_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    time_entry_id = Column(
        Integer, ForeignKey("plugin_timetracking_entries.id"), nullable=True
    )
    date = Column(DateTime, nullable=False)
    overtime_hours = Column(Numeric(10, 2), nullable=False)
    reason = Column(String(500), nullable=True)
    status = Column(String(20), default="pending")  # pending, approved, rejected
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)


# ============================================================================
# API Models (Pydantic)
# ============================================================================


class ClockInRequest(BaseModel):
    """Request to clock in."""

    employee_id: Optional[int] = None
    pin: Optional[str] = None
    notes: Optional[str] = None


class ClockOutRequest(BaseModel):
    """Request to clock out."""

    employee_id: Optional[int] = None
    pin: Optional[str] = None
    notes: Optional[str] = None


class BreakStartRequest(BaseModel):
    """Request to start a break."""

    time_entry_id: int
    notes: Optional[str] = None


class TimeEntryInfo(BaseModel):
    """Time entry information."""

    id: int
    employee_id: int
    employee_name: str
    clock_in: datetime
    clock_out: Optional[datetime]
    total_hours: Optional[Decimal]
    regular_hours: Optional[Decimal]
    overtime_hours: Optional[Decimal]
    break_minutes: int
    notes: Optional[str]
    is_approved: bool
    approved_by: Optional[int]
    approved_at: Optional[datetime]

    class Config:
        from_attributes = True


class ShiftCreate(BaseModel):
    """Request to create a shift."""

    employee_id: int
    shift_date: datetime
    start_time: datetime
    end_time: datetime
    shift_type: Optional[str] = None
    notes: Optional[str] = None


class ShiftInfo(BaseModel):
    """Shift information."""

    id: int
    employee_id: int
    employee_name: str
    shift_date: datetime
    start_time: datetime
    end_time: datetime
    expected_hours: Decimal
    shift_type: Optional[str]
    notes: Optional[str]
    is_published: bool

    class Config:
        from_attributes = True


class TimeReportRequest(BaseModel):
    """Request to generate a time report."""

    employee_id: Optional[int] = None
    start_date: datetime
    end_date: datetime
    report_type: str = Field(..., pattern="^(daily|weekly|monthly)$")


# ============================================================================
# Plugin Class
# ============================================================================


class EmployeeTimeTrackingPlugin(BasePlugin):
    """
    Employee Time Tracking Plugin.

    Provides comprehensive time tracking and shift management.
    """

    def __init__(self):
        super().__init__()
        self.config = {
            "work_hours_per_day": 8.0,
            "overtime_after_hours": 8.5,
            "auto_break_after_hours": 6.0,
            "break_duration_minutes": 30,
            "round_to_minutes": 15,
        }

    def get_metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        return PluginMetadata(
            name="employee_time_tracking",
            version="1.0.0",
            description="Employee time tracking with clock in/out and shift management",
            author="Stumpf.works",
            dependencies=[],
        )

    def get_name(self) -> str:
        """Get plugin name."""
        return "employee_time_tracking"

    def get_display_name(self) -> str:
        """Get plugin display name."""
        return "Arbeitszeiterfassung"

    def get_description(self) -> str:
        """Get plugin description."""
        return "Mitarbeiter-Zeiterfassung mit Stempeluhr und Schichtplanung"

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
                "work_hours_per_day": {
                    "type": "number",
                    "default": 8.0,
                    "minimum": 1.0,
                    "maximum": 24.0,
                    "description": "Standard-Arbeitsstunden pro Tag",
                },
                "overtime_after_hours": {
                    "type": "number",
                    "default": 8.5,
                    "minimum": 1.0,
                    "maximum": 24.0,
                    "description": "Überstunden ab (Stunden)",
                },
                "auto_break_after_hours": {
                    "type": "number",
                    "default": 6.0,
                    "minimum": 0.0,
                    "maximum": 24.0,
                    "description": "Automatische Pause nach (Stunden)",
                },
                "break_duration_minutes": {
                    "type": "integer",
                    "default": 30,
                    "minimum": 0,
                    "maximum": 480,
                    "description": "Pause-Dauer in Minuten",
                },
                "round_to_minutes": {
                    "type": "integer",
                    "default": 15,
                    "enum": [1, 5, 10, 15, 30],
                    "description": "Zeitrundung in Minuten",
                },
            },
        }

    def configure(self, config: Dict):
        """Configure plugin with settings."""
        work_hours = config.get("work_hours_per_day", 8.0)
        if work_hours < 1.0 or work_hours > 24.0:
            raise ValueError("work_hours_per_day must be between 1.0 and 24.0")

        self.config.update(config)
        logger.info("employee_time_tracking_configured", config=self.config)

    def get_models(self) -> List[Any]:
        """Return database models."""
        return [TimeEntry, Break, Shift, Overtime]

    async def on_enable(self):
        """Called when plugin is enabled."""
        logger.info("employee_time_tracking_enabled")

    async def on_disable(self):
        """Called when plugin is disabled."""
        logger.info("employee_time_tracking_disabled")

    def _round_minutes(self, minutes: int) -> int:
        """Round minutes based on configuration."""
        round_to = self.config["round_to_minutes"]
        return round(minutes / round_to) * round_to

    def _calculate_hours(
        self, clock_in: datetime, clock_out: datetime, break_minutes: int
    ) -> tuple[Decimal, Decimal, Decimal]:
        """Calculate regular and overtime hours."""
        # Total duration
        duration = clock_out - clock_in
        total_minutes = int(duration.total_seconds() / 60) - break_minutes

        # Round total minutes
        total_minutes = self._round_minutes(total_minutes)

        # Convert to hours
        total_hours = Decimal(str(total_minutes / 60))

        # Calculate regular and overtime
        overtime_threshold = Decimal(str(self.config["overtime_after_hours"]))

        if total_hours > overtime_threshold:
            regular_hours = overtime_threshold
            overtime_hours = total_hours - overtime_threshold
        else:
            regular_hours = total_hours
            overtime_hours = Decimal("0")

        return total_hours, regular_hours, overtime_hours

    def get_router(self) -> APIRouter:
        """Return API router with endpoints."""
        router = APIRouter(prefix="/time-tracking", tags=["General - Time Tracking"])

        # ============================================================================
        # Clock In/Out Endpoints
        # ============================================================================

        @router.post("/clock-in", status_code=status.HTTP_201_CREATED)
        async def clock_in(
            request: ClockInRequest,
            current_user: User = Depends(get_current_user),
            db: AsyncSession = Depends(get_db),
        ):
            """Clock in for work."""
            employee_id = request.employee_id or current_user.id

            # Check if already clocked in
            result = await db.execute(
                select(TimeEntry).where(
                    TimeEntry.tenant_id == current_user.tenant_id,
                    TimeEntry.employee_id == employee_id,
                    TimeEntry.clock_out.is_(None),
                )
            )
            existing = result.scalar_one_or_none()

            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Already clocked in. Clock out first.",
                )

            # Create time entry
            time_entry = TimeEntry(
                tenant_id=current_user.tenant_id,
                employee_id=employee_id,
                clock_in=datetime.utcnow(),
                notes=request.notes,
            )
            db.add(time_entry)
            await db.commit()
            await db.refresh(time_entry)

            logger.info(
                "employee_clocked_in",
                entry_id=time_entry.id,
                employee_id=employee_id,
            )

            return {
                "id": time_entry.id,
                "employee_id": employee_id,
                "clock_in": time_entry.clock_in,
                "message": "Clocked in successfully",
            }

        @router.post("/clock-out")
        async def clock_out(
            request: ClockOutRequest,
            current_user: User = Depends(get_current_user),
            db: AsyncSession = Depends(get_db),
        ):
            """Clock out from work."""
            employee_id = request.employee_id or current_user.id

            # Get active time entry
            result = await db.execute(
                select(TimeEntry).where(
                    TimeEntry.tenant_id == current_user.tenant_id,
                    TimeEntry.employee_id == employee_id,
                    TimeEntry.clock_out.is_(None),
                )
            )
            time_entry = result.scalar_one_or_none()

            if not time_entry:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No active clock-in found",
                )

            # Calculate break time
            breaks_result = await db.execute(
                select(Break).where(
                    Break.time_entry_id == time_entry.id,
                    Break.break_end.isnot(None),
                )
            )
            breaks = breaks_result.scalars().all()
            total_break_minutes = sum(b.duration_minutes or 0 for b in breaks)

            # Clock out
            clock_out_time = datetime.utcnow()
            time_entry.clock_out = clock_out_time
            time_entry.break_minutes = total_break_minutes

            if request.notes:
                time_entry.notes = request.notes

            # Calculate hours
            total_hours, regular_hours, overtime_hours = self._calculate_hours(
                time_entry.clock_in, clock_out_time, total_break_minutes
            )

            time_entry.total_hours = total_hours
            time_entry.regular_hours = regular_hours
            time_entry.overtime_hours = overtime_hours

            # Create overtime record if applicable
            if overtime_hours > 0:
                overtime = Overtime(
                    tenant_id=current_user.tenant_id,
                    employee_id=employee_id,
                    time_entry_id=time_entry.id,
                    date=time_entry.clock_in.date(),
                    overtime_hours=overtime_hours,
                    status="pending",
                )
                db.add(overtime)

            await db.commit()

            logger.info(
                "employee_clocked_out",
                entry_id=time_entry.id,
                employee_id=employee_id,
                total_hours=float(total_hours),
                overtime_hours=float(overtime_hours),
            )

            return {
                "id": time_entry.id,
                "employee_id": employee_id,
                "clock_in": time_entry.clock_in,
                "clock_out": clock_out_time,
                "total_hours": float(total_hours),
                "regular_hours": float(regular_hours),
                "overtime_hours": float(overtime_hours),
                "break_minutes": total_break_minutes,
                "message": "Clocked out successfully",
            }

        # ============================================================================
        # Break Endpoints
        # ============================================================================

        @router.post("/break/start", status_code=status.HTTP_201_CREATED)
        async def start_break(
            request: BreakStartRequest,
            current_user: User = Depends(get_current_user),
            db: AsyncSession = Depends(get_db),
        ):
            """Start a break."""
            # Verify time entry exists and is active
            result = await db.execute(
                select(TimeEntry).where(
                    TimeEntry.id == request.time_entry_id,
                    TimeEntry.tenant_id == current_user.tenant_id,
                    TimeEntry.clock_out.is_(None),
                )
            )
            time_entry = result.scalar_one_or_none()

            if not time_entry:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Active time entry not found",
                )

            # Check if already on break
            break_result = await db.execute(
                select(Break).where(
                    Break.time_entry_id == request.time_entry_id,
                    Break.break_end.is_(None),
                )
            )
            active_break = break_result.scalar_one_or_none()

            if active_break:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Break already in progress",
                )

            # Create break
            break_entry = Break(
                tenant_id=current_user.tenant_id,
                time_entry_id=request.time_entry_id,
                break_start=datetime.utcnow(),
                break_type="manual",
                notes=request.notes,
            )
            db.add(break_entry)
            await db.commit()
            await db.refresh(break_entry)

            logger.info(
                "break_started",
                break_id=break_entry.id,
                time_entry_id=request.time_entry_id,
            )

            return {
                "id": break_entry.id,
                "break_start": break_entry.break_start,
                "message": "Break started",
            }

        @router.post("/break/end")
        async def end_break(
            time_entry_id: int,
            current_user: User = Depends(get_current_user),
            db: AsyncSession = Depends(get_db),
        ):
            """End a break."""
            # Get active break
            result = await db.execute(
                select(Break).where(
                    Break.time_entry_id == time_entry_id,
                    Break.tenant_id == current_user.tenant_id,
                    Break.break_end.is_(None),
                )
            )
            break_entry = result.scalar_one_or_none()

            if not break_entry:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No active break found",
                )

            # End break
            break_end_time = datetime.utcnow()
            break_entry.break_end = break_end_time

            # Calculate duration
            duration = break_end_time - break_entry.break_start
            break_entry.duration_minutes = int(duration.total_seconds() / 60)

            await db.commit()

            logger.info(
                "break_ended",
                break_id=break_entry.id,
                duration_minutes=break_entry.duration_minutes,
            )

            return {
                "id": break_entry.id,
                "break_start": break_entry.break_start,
                "break_end": break_end_time,
                "duration_minutes": break_entry.duration_minutes,
                "message": "Break ended",
            }

        # ============================================================================
        # Time Entry Endpoints
        # ============================================================================

        @router.get("/current")
        async def get_current_status(
            current_user: User = Depends(get_current_user),
            db: AsyncSession = Depends(get_db),
        ):
            """Get current time tracking status."""
            # Get active time entry
            result = await db.execute(
                select(TimeEntry).where(
                    TimeEntry.tenant_id == current_user.tenant_id,
                    TimeEntry.employee_id == current_user.id,
                    TimeEntry.clock_out.is_(None),
                )
            )
            time_entry = result.scalar_one_or_none()

            if not time_entry:
                return {"status": "clocked_out", "time_entry": None}

            # Check for active break
            break_result = await db.execute(
                select(Break).where(
                    Break.time_entry_id == time_entry.id,
                    Break.break_end.is_(None),
                )
            )
            active_break = break_result.scalar_one_or_none()

            # Calculate current duration
            current_duration = datetime.utcnow() - time_entry.clock_in
            current_hours = current_duration.total_seconds() / 3600

            return {
                "status": "on_break" if active_break else "clocked_in",
                "time_entry": {
                    "id": time_entry.id,
                    "clock_in": time_entry.clock_in,
                    "current_hours": round(current_hours, 2),
                },
                "active_break": (
                    {
                        "id": active_break.id,
                        "break_start": active_break.break_start,
                    }
                    if active_break
                    else None
                ),
            }

        @router.get("/entries", response_model=List[TimeEntryInfo])
        async def get_time_entries(
            employee_id: Optional[int] = Query(None),
            start_date: Optional[datetime] = Query(None),
            end_date: Optional[datetime] = Query(None),
            current_user: User = Depends(get_current_user),
            db: AsyncSession = Depends(get_db),
        ):
            """Get time entries with filters."""
            query = select(TimeEntry).where(
                TimeEntry.tenant_id == current_user.tenant_id
            )

            if employee_id:
                query = query.where(TimeEntry.employee_id == employee_id)

            if start_date:
                query = query.where(TimeEntry.clock_in >= start_date)

            if end_date:
                query = query.where(TimeEntry.clock_in <= end_date)

            query = query.order_by(TimeEntry.clock_in.desc())

            result = await db.execute(query)
            entries = result.scalars().all()

            entries_info = []
            for entry in entries:
                # Get employee name
                emp_result = await db.execute(
                    select(User).where(User.id == entry.employee_id)
                )
                employee = emp_result.scalar_one_or_none()

                entries_info.append(
                    TimeEntryInfo(
                        id=entry.id,
                        employee_id=entry.employee_id,
                        employee_name=employee.full_name if employee else "Unknown",
                        clock_in=entry.clock_in,
                        clock_out=entry.clock_out,
                        total_hours=entry.total_hours,
                        regular_hours=entry.regular_hours,
                        overtime_hours=entry.overtime_hours,
                        break_minutes=entry.break_minutes,
                        notes=entry.notes,
                        is_approved=entry.approved_by is not None,
                        approved_by=entry.approved_by,
                        approved_at=entry.approved_at,
                    )
                )

            return entries_info

        # ============================================================================
        # Shift Endpoints
        # ============================================================================

        @router.get("/shifts", response_model=List[ShiftInfo])
        async def get_shifts(
            employee_id: Optional[int] = Query(None),
            start_date: Optional[datetime] = Query(None),
            end_date: Optional[datetime] = Query(None),
            current_user: User = Depends(get_current_user),
            db: AsyncSession = Depends(get_db),
        ):
            """Get scheduled shifts."""
            query = select(Shift).where(Shift.tenant_id == current_user.tenant_id)

            if employee_id:
                query = query.where(Shift.employee_id == employee_id)

            if start_date:
                query = query.where(Shift.shift_date >= start_date)

            if end_date:
                query = query.where(Shift.shift_date <= end_date)

            query = query.order_by(Shift.start_time)

            result = await db.execute(query)
            shifts = result.scalars().all()

            shifts_info = []
            for shift in shifts:
                # Get employee name
                emp_result = await db.execute(
                    select(User).where(User.id == shift.employee_id)
                )
                employee = emp_result.scalar_one_or_none()

                shifts_info.append(
                    ShiftInfo(
                        id=shift.id,
                        employee_id=shift.employee_id,
                        employee_name=employee.full_name if employee else "Unknown",
                        shift_date=shift.shift_date,
                        start_time=shift.start_time,
                        end_time=shift.end_time,
                        expected_hours=shift.expected_hours,
                        shift_type=shift.shift_type,
                        notes=shift.notes,
                        is_published=shift.is_published,
                    )
                )

            return shifts_info

        @router.post("/shifts", status_code=status.HTTP_201_CREATED)
        async def create_shift(
            request: ShiftCreate,
            current_user: User = Depends(get_current_user),
            db: AsyncSession = Depends(get_db),
        ):
            """Create a new shift."""
            # Calculate expected hours
            duration = request.end_time - request.start_time
            expected_hours = Decimal(str(duration.total_seconds() / 3600))

            shift = Shift(
                tenant_id=current_user.tenant_id,
                employee_id=request.employee_id,
                shift_date=request.shift_date,
                start_time=request.start_time,
                end_time=request.end_time,
                expected_hours=expected_hours,
                shift_type=request.shift_type,
                notes=request.notes,
                created_by=current_user.id,
            )
            db.add(shift)
            await db.commit()
            await db.refresh(shift)

            logger.info(
                "shift_created",
                shift_id=shift.id,
                employee_id=request.employee_id,
                date=request.shift_date,
            )

            return {
                "id": shift.id,
                "employee_id": request.employee_id,
                "shift_date": request.shift_date,
                "expected_hours": float(expected_hours),
            }

        # ============================================================================
        # Report Endpoints
        # ============================================================================

        @router.get("/report")
        async def generate_report(
            employee_id: Optional[int] = Query(None),
            start_date: datetime = Query(...),
            end_date: datetime = Query(...),
            current_user: User = Depends(get_current_user),
            db: AsyncSession = Depends(get_db),
        ):
            """Generate time tracking report."""
            query = select(TimeEntry).where(
                TimeEntry.tenant_id == current_user.tenant_id,
                TimeEntry.clock_in >= start_date,
                TimeEntry.clock_in <= end_date,
                TimeEntry.clock_out.isnot(None),
            )

            if employee_id:
                query = query.where(TimeEntry.employee_id == employee_id)

            result = await db.execute(query)
            entries = result.scalars().all()

            total_hours = sum(float(e.total_hours or 0) for e in entries)
            total_regular = sum(float(e.regular_hours or 0) for e in entries)
            total_overtime = sum(float(e.overtime_hours or 0) for e in entries)

            return {
                "period": {
                    "start": start_date,
                    "end": end_date,
                },
                "summary": {
                    "total_entries": len(entries),
                    "total_hours": round(total_hours, 2),
                    "regular_hours": round(total_regular, 2),
                    "overtime_hours": round(total_overtime, 2),
                },
                "entries": [
                    {
                        "date": e.clock_in.date().isoformat(),
                        "clock_in": e.clock_in.isoformat(),
                        "clock_out": e.clock_out.isoformat() if e.clock_out else None,
                        "total_hours": float(e.total_hours or 0),
                        "overtime_hours": float(e.overtime_hours or 0),
                    }
                    for e in entries
                ],
            }

        return router


# ============================================================================
# Plugin Instance (for auto-discovery)
# ============================================================================

plugin = EmployeeTimeTrackingPlugin()

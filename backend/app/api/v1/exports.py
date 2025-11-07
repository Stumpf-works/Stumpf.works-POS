"""
Export API Endpoints
GoBD/DSFinV-K compliant data exports
"""

from datetime import datetime, timedelta

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, require_admin
from app.core.database import get_sync_db
from app.models.user import User
from app.services.export.dsfink_exporter import DSFinVKExporter

logger = structlog.get_logger()
router = APIRouter(prefix="/exports", tags=["Exports"])


@router.get("/dsfink")
async def export_dsfink(
    start_date: datetime = Query(..., description="Start date for export (ISO 8601)"),
    end_date: datetime = Query(..., description="End date for export (ISO 8601)"),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_sync_db),
):
    """
    Export transaction data in DSFinV-K format.

    Returns a TAR.GZ archive containing CSV files for:
    - Locations (stamm_orte.csv)
    - Cash registers (stamm_kassen.csv)
    - Employees (stamm_mitarbeiter.csv)
    - Products (stamm_artikel.csv)
    - Transaction headers (bonkopf.csv)
    - Transaction items (bonpos.csv)
    - TSE transactions (tse_transaktionen.csv)

    This export format is compliant with German tax authority requirements
    and can be submitted during tax audits (Betriebsprüfung).
    """
    # Validate date range
    if start_date >= end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start date must be before end date",
        )

    # Limit export range (max 1 year)
    max_range = timedelta(days=365)
    if (end_date - start_date) > max_range:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Export range cannot exceed 1 year",
        )

    logger.info(
        "dsfink_export_requested",
        tenant_id=current_user.tenant_id,
        start_date=start_date,
        end_date=end_date,
        user_id=current_user.id,
    )

    try:
        # Create exporter
        exporter = DSFinVKExporter(tenant_id=current_user.tenant_id, db=db)

        # Generate export
        export_data = exporter.export(start_date=start_date, end_date=end_date)

        # Generate filename
        filename = (
            f"dsfink_export_{current_user.tenant_id}_"
            f"{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.tar.gz"
        )

        logger.info(
            "dsfink_export_completed",
            tenant_id=current_user.tenant_id,
            filename=filename,
            size_bytes=len(export_data),
        )

        # Return TAR.GZ file
        return Response(
            content=export_data,
            media_type="application/gzip",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )

    except Exception as e:
        logger.exception(
            "dsfink_export_error",
            tenant_id=current_user.tenant_id,
            error=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Export failed: {str(e)}",
        )


@router.get("/transactions/csv")
async def export_transactions_csv(
    start_date: datetime = Query(..., description="Start date for export"),
    end_date: datetime = Query(..., description="End date for export"),
    current_user: User = Depends(get_current_user),
):
    """
    Export transactions as simple CSV file.

    This is a simplified export format for basic reporting.
    For tax compliance, use /exports/dsfink instead.
    """
    # TODO: Implement simple CSV export
    # This can be used for basic reporting and analytics

    return {"message": "CSV export not yet implemented"}

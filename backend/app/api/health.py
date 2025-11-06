"""
Health Check Endpoints
Provides health, readiness, and liveness checks for monitoring
"""

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime
import httpx
import structlog

from app.core.database import get_db
from app.core.config import settings

logger = structlog.get_logger()
router = APIRouter(tags=["Health"])


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """
    Basic health check - returns 200 if app is running.
    Used for basic uptime monitoring.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
    }


@router.get("/readiness", status_code=status.HTTP_200_OK)
async def readiness_check(db: AsyncSession = Depends(get_db)):
    """
    Readiness check - verifies all dependencies are ready.
    Returns 200 if ready to accept traffic, 503 if not.

    Checks:
    - Database connectivity
    - Redis connectivity
    - Essential services

    Used by load balancers to determine if instance should receive traffic.
    """
    checks = {
        "database": False,
        "redis": False,
        "fiskaly": None,  # Optional
        "sumup": None,    # Optional
    }
    overall_status = "ready"
    status_code = status.HTTP_200_OK

    # Check database
    try:
        result = await db.execute(text("SELECT 1"))
        checks["database"] = result.scalar() == 1
    except Exception as e:
        checks["database"] = False
        overall_status = "not_ready"
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        logger.error("readiness_check_failed", component="database", error=str(e))

    # Check Redis
    try:
        import redis.asyncio as redis
        redis_client = redis.from_url(settings.REDIS_URL)
        await redis_client.ping()
        checks["redis"] = True
        await redis_client.close()
    except Exception as e:
        checks["redis"] = False
        overall_status = "not_ready"
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        logger.error("readiness_check_failed", component="redis", error=str(e))

    # Check Fiskaly (optional - don't fail if down)
    if settings.TSE_ENABLED:
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                response = await client.get("https://kassensichv.io")
                checks["fiskaly"] = response.status_code == 200
        except Exception:
            checks["fiskaly"] = False  # Not critical

    # Check SumUp (optional - don't fail if down)
    if settings.SUMUP_ENABLED:
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                response = await client.get("https://api.sumup.com")
                checks["sumup"] = response.status_code in [200, 404]  # 404 is ok
        except Exception:
            checks["sumup"] = False  # Not critical

    response_data = {
        "status": overall_status,
        "timestamp": datetime.utcnow().isoformat(),
        "checks": checks,
    }

    return JSONResponse(
        status_code=status_code,
        content=response_data
    )


@router.get("/liveness", status_code=status.HTTP_200_OK)
async def liveness_check():
    """
    Liveness check - verifies app is alive (not deadlocked).
    Returns 200 if alive, 503 if dead.

    This is a simple check - if we can respond, we're alive.
    Used by orchestrators (Kubernetes) to restart dead instances.
    """
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/metrics", status_code=status.HTTP_200_OK)
async def metrics_endpoint(db: AsyncSession = Depends(get_db)):
    """
    Application metrics endpoint.
    Returns key metrics for monitoring dashboards.
    """
    metrics = {
        "timestamp": datetime.utcnow().isoformat(),
        "app": "stumpf-pos",
        "environment": settings.ENVIRONMENT,
    }

    try:
        # Count active tenants
        result = await db.execute(text("SELECT COUNT(*) FROM public.tenants"))
        metrics["active_tenants"] = result.scalar()

        # Count total transactions (last 24h)
        result = await db.execute(text("""
            SELECT COUNT(*)
            FROM public.transactions
            WHERE completed_at >= NOW() - INTERVAL '24 hours'
        """))
        metrics["transactions_24h"] = result.scalar()

        # Count pending TSE signatures
        result = await db.execute(text("""
            SELECT COUNT(*)
            FROM public.transactions
            WHERE status = 'completed' AND is_tse_signed = false
        """))
        metrics["pending_tse_signatures"] = result.scalar()

    except Exception as e:
        logger.error("metrics_collection_failed", error=str(e))
        metrics["error"] = "Failed to collect some metrics"

    return metrics


@router.get("/status", status_code=status.HTTP_200_OK)
async def detailed_status(db: AsyncSession = Depends(get_db)):
    """
    Detailed status endpoint with system information.
    For operational dashboards and debugging.
    """
    import psutil
    import platform

    status_info = {
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "uptime_seconds": None,
        "system": {
            "platform": platform.system(),
            "python_version": platform.python_version(),
            "cpu_count": psutil.cpu_count(),
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
        },
        "database": {
            "connected": False,
            "pool_size": None,
        },
        "features": {
            "tse_enabled": settings.TSE_ENABLED,
            "sumup_enabled": settings.SUMUP_ENABLED,
            "multi_tenant": True,
            "offline_mode": True,
        }
    }

    # Check database
    try:
        result = await db.execute(text("SELECT version()"))
        db_version = result.scalar()
        status_info["database"]["connected"] = True
        status_info["database"]["version"] = db_version
    except Exception as e:
        status_info["database"]["error"] = str(e)

    return status_info

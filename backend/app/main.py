"""
Stumpf.works POS - Main Application Entry Point
FastAPI application with multi-tenant support, Cloud-TSE, and SumUp integration
"""

from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import close_db, init_db
from app.core.error_tracking import capture_exception, configure_error_tracking
from app.core.logging_config import LoggingMiddleware, configure_logging
from app.middleware.cors import configure_cors
from app.middleware.rate_limit import RateLimitMiddleware, rate_limiter
from app.middleware.security import (RequestIDMiddleware,
                                     SecurityAuditMiddleware,
                                     SecurityHeadersMiddleware,
                                     SQLInjectionProtectionMiddleware)
# Import Middleware
from app.middleware.tenant import TenantMiddleware
from app.plugins import plugin_registry

# Configure structured logging
configure_logging()
logger = structlog.get_logger()

# Configure error tracking (Sentry)
configure_error_tracking()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info(
        "application_starting",
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
        debug=settings.DEBUG,
    )

    # Initialize database (only in development, use Alembic in production)
    if settings.is_development:
        logger.info("initializing_database")
        try:
            await init_db()
        except Exception as e:
            logger.error("database_init_failed", error=str(e), exc_info=True)

    # Start rate limiter cleanup task
    if settings.RATE_LIMIT_ENABLED:
        import asyncio

        asyncio.create_task(rate_limiter.cleanup_old_entries())
        logger.info("rate_limiter_enabled", per_minute=settings.RATE_LIMIT_PER_MINUTE)

    # Discover and load plugins
    logger.info("discovering_plugins")
    discovered_plugins = plugin_registry.discover_plugins()
    logger.info(
        "plugins_discovered", count=len(discovered_plugins), plugins=discovered_plugins
    )

    # Load and enable plugins
    for plugin_name in discovered_plugins:
        try:
            plugin = plugin_registry.load_plugin(plugin_name)
            if plugin:
                await plugin_registry.enable_plugin(plugin_name)

                # Register plugin routes
                if plugin.get_router():
                    app.include_router(
                        plugin.get_router(), prefix=settings.API_V1_PREFIX
                    )
                    logger.info("plugin_routes_registered", plugin=plugin_name)
        except Exception as e:
            logger.error("plugin_load_failed", plugin=plugin_name, error=str(e))

    # Startup plugins
    try:
        await plugin_registry.startup_plugins()
    except Exception as e:
        logger.error("plugin_startup_failed", error=str(e))

    logger.info(
        "application_started",
        features={
            "tse_enabled": settings.TSE_ENABLED,
            "sumup_enabled": settings.SUMUP_ENABLED,
            "rate_limiting": settings.RATE_LIMIT_ENABLED,
            "sentry": bool(settings.SENTRY_DSN),
        },
    )

    yield

    # Shutdown
    logger.info("application_shutting_down")

    # Shutdown plugins
    try:
        await plugin_registry.shutdown_plugins()
    except Exception as e:
        logger.error("plugin_shutdown_failed", error=str(e))

    await close_db()
    logger.info("application_shutdown_complete")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Multi-Tenant Cloud POS System for German Market (GoBD/KassenSichV compliant)",
    docs_url="/api/docs" if not settings.is_production else None,
    redoc_url="/api/redoc" if not settings.is_production else None,
    openapi_url="/api/openapi.json" if not settings.is_production else None,
    lifespan=lifespan,
)


# ==========================================
# Middleware Configuration (Order Matters!)
# ==========================================

# 1. Security Headers (first, affects all responses)
app.add_middleware(SecurityHeadersMiddleware)

# 2. Request ID (for tracing)
app.add_middleware(RequestIDMiddleware)

# 3. CORS
app = configure_cors(app)

# 4. GZip Compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# 5. Rate Limiting (before authentication)
if settings.RATE_LIMIT_ENABLED:
    app.add_middleware(
        RateLimitMiddleware,
        requests_per_minute=settings.RATE_LIMIT_PER_MINUTE,
        burst_size=10,
    )

# 6. Security Audit (log security events)
app.add_middleware(SecurityAuditMiddleware)

# 7. SQL Injection Protection (basic detection)
app.add_middleware(SQLInjectionProtectionMiddleware)

# 8. Custom Middleware
app.add_middleware(TenantMiddleware)
app.add_middleware(LoggingMiddleware)


# ==========================================
# Exception Handlers
# ==========================================


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with proper logging."""
    logger.warning(
        "validation_error",
        path=request.url.path,
        method=request.method,
        errors=exc.errors(),
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation error",
            "errors": exc.errors(),
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.exception(
        "unhandled_exception",
        path=request.url.path,
        method=request.method,
        exception_type=type(exc).__name__,
        exception_message=str(exc),
    )

    # Send to Sentry
    capture_exception(
        exc,
        extra={
            "path": request.url.path,
            "method": request.method,
            "query_params": dict(request.query_params),
        },
    )

    # Return generic error in production
    if settings.is_production:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": str(exc),
                "type": type(exc).__name__,
            },
        )


# ==========================================
# Root Endpoints
# ==========================================


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint - API information."""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "docs": "/api/docs" if not settings.is_production else "disabled",
        "status": "operational",
    }


# ==========================================
# API Routers
# ==========================================

from app.api.health import router as health_router
from app.api.v1.router import api_router

# Include API routes
app.include_router(api_router, prefix=settings.API_V1_PREFIX)

# Include health check routes (at root level)
app.include_router(health_router, tags=["Health"])

logger.info(
    "api_routers_registered",
    api_prefix=settings.API_V1_PREFIX,
    health_endpoints=["/ health", "/readiness", "/liveness", "/metrics", "/status"],
)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=not settings.is_production,  # Disable access log in production (we have our own)
    )

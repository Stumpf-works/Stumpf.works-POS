"""
Stumpf.works POS - Main Application Entry Point
FastAPI application with multi-tenant support, Cloud-TSE, and SumUp integration
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import structlog

from app.core.config import settings
from app.core.database import init_db, close_db
from app.middleware.tenant import TenantMiddleware
from app.middleware.logging import LoggingMiddleware
from app.plugins import plugin_registry

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer() if settings.LOG_FORMAT == "json"
        else structlog.dev.ConsoleRenderer()
    ],
    wrapper_class=structlog.make_filtering_bound_logger(
        getattr(structlog.stdlib, settings.LOG_LEVEL)
    ),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info(
        "starting_application",
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT
    )

    # Initialize database (only in development, use Alembic in production)
    if settings.is_development:
        logger.info("initializing_database")
        await init_db()

    # Discover and load plugins
    logger.info("discovering_plugins")
    discovered_plugins = plugin_registry.discover_plugins()
    logger.info("plugins_discovered", count=len(discovered_plugins), plugins=discovered_plugins)

    # Load and enable plugins
    for plugin_name in discovered_plugins:
        plugin = plugin_registry.load_plugin(plugin_name)
        if plugin:
            await plugin_registry.enable_plugin(plugin_name)

            # Register plugin routes
            if plugin.get_router():
                app.include_router(plugin.get_router(), prefix=settings.API_V1_PREFIX)
                logger.info("plugin_routes_registered", plugin=plugin_name)

    # Startup plugins
    await plugin_registry.startup_plugins()

    logger.info("application_started")

    yield

    # Shutdown
    logger.info("shutting_down_application")

    # Shutdown plugins
    await plugin_registry.shutdown_plugins()

    await close_db()
    logger.info("application_shutdown_complete")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Multi-Tenant Cloud POS System for German Market (GoBD/KassenSichV compliant)",
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
    openapi_url="/openapi.json" if not settings.is_production else None,
    lifespan=lifespan,
)


# ==========================================
# Middleware Configuration
# ==========================================

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_CREDENTIALS,
    allow_methods=settings.CORS_METHODS,
    allow_headers=settings.CORS_HEADERS,
)

# GZip Compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Custom Middleware
app.add_middleware(TenantMiddleware)
app.add_middleware(LoggingMiddleware)


# ==========================================
# Exception Handlers
# ==========================================

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with proper logging."""
    logger.error(
        "validation_error",
        path=request.url.path,
        errors=exc.errors(),
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": exc.errors(),
            "body": exc.body if hasattr(exc, 'body') else None
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.exception(
        "unhandled_exception",
        path=request.url.path,
        exception=str(exc),
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error" if settings.is_production else str(exc)
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
        "docs": "/docs" if not settings.is_production else "disabled",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


@app.get("/ready", tags=["Health"])
async def readiness_check():
    """Readiness check for Kubernetes/Docker health probes."""
    # TODO: Add checks for database, redis, external services
    return {
        "status": "ready",
        "checks": {
            "database": "ok",
            "redis": "ok",
        }
    }


# ==========================================
# API Routers
# ==========================================

from app.api.v1.router import api_router

app.include_router(api_router, prefix=settings.API_V1_PREFIX)

logger.info("api_routers_registered", prefix=settings.API_V1_PREFIX)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )

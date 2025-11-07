"""
Structured Logging Configuration
Uses structlog for structured, JSON-formatted logging
"""

import logging
import sys
from typing import Any

import structlog
from structlog.types import EventDict, WrappedLogger

from app.core.config import settings


def add_app_context(
    logger: WrappedLogger, method_name: str, event_dict: EventDict
) -> EventDict:
    """
    Add application context to all log messages.
    """
    event_dict["app"] = "stumpf-pos"
    event_dict["environment"] = settings.ENVIRONMENT
    return event_dict


def censor_sensitive_data(
    logger: WrappedLogger, method_name: str, event_dict: EventDict
) -> EventDict:
    """
    Censor sensitive data from logs.
    """
    sensitive_keys = {
        "password",
        "pin",
        "token",
        "api_key",
        "api_secret",
        "secret",
        "authorization",
    }

    def censor_dict(d: dict) -> dict:
        """Recursively censor sensitive keys."""
        result = {}
        for key, value in d.items():
            if key.lower() in sensitive_keys:
                result[key] = "***CENSORED***"
            elif isinstance(value, dict):
                result[key] = censor_dict(value)
            else:
                result[key] = value
        return result

    return censor_dict(event_dict)


def configure_logging():
    """
    Configure structured logging with structlog.
    """

    # Determine log level
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )

    # Silence noisy loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    # Structlog processors
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        add_app_context,
        censor_sensitive_data,
        structlog.processors.StackInfoRenderer(),
    ]

    if settings.ENVIRONMENT == "development":
        # Pretty console output for development
        processors = shared_processors + [structlog.dev.ConsoleRenderer()]
    else:
        # JSON output for production (easier to parse)
        processors = shared_processors + [
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


class LoggingMiddleware:
    """
    Middleware for logging all requests and responses.
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, request, call_next):
        import time

        from fastapi import Request

        logger = structlog.get_logger()

        # Skip logging for health checks
        if request.url.path in ["/health", "/readiness"]:
            return await call_next(request)

        # Start timer
        start_time = time.time()

        # Extract request info
        request_info = {
            "method": request.method,
            "path": request.url.path,
            "query_params": str(request.url.query) if request.url.query else None,
            "client_ip": self._get_client_ip(request),
            "user_agent": request.headers.get("User-Agent"),
            "request_id": getattr(request.state, "request_id", None),
        }

        # Add tenant ID if available
        tenant_id = request.headers.get("X-Tenant-ID")
        if tenant_id:
            request_info["tenant_id"] = tenant_id

        # Log request
        logger.info("request_started", **request_info)

        try:
            # Process request
            response = await call_next(request)

            # Calculate duration
            duration = time.time() - start_time

            # Log response
            logger.info(
                "request_completed",
                **request_info,
                status_code=response.status_code,
                duration_ms=round(duration * 1000, 2),
            )

            return response

        except Exception as exc:
            # Calculate duration
            duration = time.time() - start_time

            # Log error
            logger.error(
                "request_failed",
                **request_info,
                duration_ms=round(duration * 1000, 2),
                error=str(exc),
                error_type=type(exc).__name__,
                exc_info=True,
            )
            raise

    def _get_client_ip(self, request) -> str:
        """Extract client IP from request."""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return request.client.host if request.client else "unknown"


# Helper functions for application code


def log_business_event(event_name: str, **kwargs):
    """
    Log a business event (e.g., transaction created, user registered).
    """
    logger = structlog.get_logger()
    logger.info("business_event", event=event_name, **kwargs)


def log_security_event(event_name: str, severity: str = "info", **kwargs):
    """
    Log a security event (e.g., login attempt, permission denied).
    """
    logger = structlog.get_logger()

    log_method = getattr(logger, severity.lower(), logger.info)
    log_method("security_event", event=event_name, **kwargs)


def log_integration_event(integration: str, event_name: str, success: bool, **kwargs):
    """
    Log an external integration event (e.g., Fiskaly API call).
    """
    logger = structlog.get_logger()

    if success:
        logger.info(
            "integration_event",
            integration=integration,
            event=event_name,
            success=True,
            **kwargs,
        )
    else:
        logger.error(
            "integration_event",
            integration=integration,
            event=event_name,
            success=False,
            **kwargs,
        )

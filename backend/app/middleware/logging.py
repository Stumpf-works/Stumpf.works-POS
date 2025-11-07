"""
Logging Middleware
Logs all HTTP requests and responses with structured logging
Includes request ID, duration, status code, etc.
"""

import time
import uuid
from typing import Callable

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = structlog.get_logger()


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all HTTP requests and responses.
    Adds request ID for tracing.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and log details."""

        # Generate unique request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # Get tenant ID if available
        tenant_id = getattr(request.state, "tenant_id", None)

        # Start timer
        start_time = time.time()

        # Log incoming request
        logger.info(
            "request_started",
            request_id=request_id,
            tenant_id=tenant_id,
            method=request.method,
            path=request.url.path,
            query_params=str(request.query_params),
            client_host=request.client.host if request.client else None,
        )

        # Process request
        try:
            response = await call_next(request)

            # Calculate duration
            duration = time.time() - start_time

            # Log response
            logger.info(
                "request_completed",
                request_id=request_id,
                tenant_id=tenant_id,
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_seconds=round(duration, 3),
            )

            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id

            return response

        except Exception as exc:
            # Calculate duration
            duration = time.time() - start_time

            # Log error
            logger.error(
                "request_failed",
                request_id=request_id,
                tenant_id=tenant_id,
                method=request.method,
                path=request.url.path,
                duration_seconds=round(duration, 3),
                exception=str(exc),
                exception_type=type(exc).__name__,
            )

            # Re-raise exception to be handled by exception handlers
            raise

"""
Security Headers Middleware
Adds security-related HTTP headers to all responses
"""

from typing import Callable

import structlog
from fastapi import Request, Response

logger = structlog.get_logger()


class SecurityHeadersMiddleware:
    """
    Middleware that adds security headers to all responses.
    Based on OWASP recommendations.
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, request: Request, call_next: Callable):
        response = await call_next(request)

        # Prevent clickjacking attacks
        response.headers["X-Frame-Options"] = "DENY"

        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Enable XSS protection
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Referrer Policy - don't leak information
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Content Security Policy
        # Adjust based on your needs
        csp_directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'",  # Adjust for production
            "style-src 'self' 'unsafe-inline'",
            "img-src 'self' data: https:",
            "font-src 'self' data:",
            "connect-src 'self' https://api.fiskaly.com https://api.sumup.com",
            "frame-ancestors 'none'",
            "base-uri 'self'",
            "form-action 'self'",
        ]
        response.headers["Content-Security-Policy"] = "; ".join(csp_directives)

        # Permissions Policy (formerly Feature-Policy)
        # Restrict access to sensitive browser features
        permissions_directives = [
            "geolocation=()",
            "microphone=()",
            "camera=()",
            "payment=(self)",  # Allow payment APIs for SumUp
            "usb=()",
            "magnetometer=()",
            "gyroscope=()",
            "accelerometer=()",
        ]
        response.headers["Permissions-Policy"] = ", ".join(permissions_directives)

        # Strict Transport Security (HSTS)
        # Only add in production with HTTPS
        # response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        return response


class RequestIDMiddleware:
    """
    Adds a unique request ID to each request for tracing.
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, request: Request, call_next: Callable):
        import uuid

        # Generate or extract request ID
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

        # Store in request state for use in logging
        request.state.request_id = request_id

        # Process request
        response = await call_next(request)

        # Add to response headers
        response.headers["X-Request-ID"] = request_id

        return response


class SecurityAuditMiddleware:
    """
    Logs security-relevant events for audit purposes.
    """

    def __init__(self, app):
        self.app = app
        self.sensitive_paths = [
            "/api/v1/auth/login",
            "/api/v1/auth/register",
            "/api/v1/admin",
        ]

    async def __call__(self, request: Request, call_next: Callable):
        # Check if this is a sensitive endpoint
        is_sensitive = any(
            request.url.path.startswith(path) for path in self.sensitive_paths
        )

        if is_sensitive:
            # Log before processing
            logger.info(
                "security_audit",
                event="sensitive_endpoint_access",
                method=request.method,
                path=request.url.path,
                client_ip=self._get_client_ip(request),
                user_agent=request.headers.get("User-Agent", "unknown"),
                request_id=getattr(request.state, "request_id", "unknown"),
            )

        response = await call_next(request)

        # Log authentication failures
        if is_sensitive and response.status_code in [401, 403]:
            logger.warning(
                "security_audit",
                event="authentication_failure",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                client_ip=self._get_client_ip(request),
                request_id=getattr(request.state, "request_id", "unknown"),
            )

        return response

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request."""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return request.client.host if request.client else "unknown"


class SQLInjectionProtectionMiddleware:
    """
    Basic SQL injection detection middleware.
    This is a last line of defense - proper parameterized queries
    should prevent SQL injection at the ORM level.
    """

    def __init__(self, app):
        self.app = app
        self.sql_patterns = [
            "' OR '1'='1",
            "' OR 1=1--",
            "'; DROP TABLE",
            "UNION SELECT",
            "1' AND '1'='1",
        ]

    async def __call__(self, request: Request, call_next: Callable):
        # Check query parameters
        query_string = str(request.url.query).upper()

        for pattern in self.sql_patterns:
            if pattern.upper() in query_string:
                logger.warning(
                    "sql_injection_attempt",
                    pattern=pattern,
                    query_string=query_string,
                    client_ip=self._get_client_ip(request),
                    path=request.url.path,
                )

                # Could return 400 Bad Request or block the request
                # For now, just log and continue (SQLAlchemy protects us)

        return await call_next(request)

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request."""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

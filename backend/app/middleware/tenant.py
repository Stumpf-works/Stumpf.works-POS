"""
Multi-Tenant Middleware
Extracts tenant information from request headers or subdomain
and sets the appropriate database schema for the request
"""

import re
from typing import Optional

import structlog
from fastapi import HTTPException, Request, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.core.config import settings
from app.core.database import TenantContext

logger = structlog.get_logger()


class TenantMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle multi-tenant routing.

    Extracts tenant identifier from:
    1. X-Tenant-ID header
    2. Subdomain (if ENABLE_SUBDOMAIN_ROUTING is True)

    Sets the PostgreSQL search_path to the tenant's schema.
    """

    EXCLUDED_PATHS = [
        "/",
        "/health",
        "/ready",
        "/docs",
        "/redoc",
        "/openapi.json",
    ]

    def _extract_tenant_from_header(self, request: Request) -> Optional[str]:
        """Extract tenant ID from request header."""
        return request.headers.get(settings.TENANT_HEADER_NAME)

    def _extract_tenant_from_subdomain(self, request: Request) -> Optional[str]:
        """
        Extract tenant ID from subdomain.
        Example: tenant1.stumpf.works -> tenant1
        """
        if not settings.ENABLE_SUBDOMAIN_ROUTING:
            return None

        host = request.headers.get("host", "")
        # Remove port if present
        host = host.split(":")[0]

        # Split by dots
        parts = host.split(".")

        # If we have at least 3 parts (subdomain.domain.tld), extract subdomain
        if len(parts) >= 3:
            subdomain = parts[0]
            # Validate subdomain format (alphanumeric and hyphens)
            if re.match(r"^[a-z0-9-]+$", subdomain):
                return subdomain

        return None

    def _validate_tenant_id(self, tenant_id: str) -> bool:
        """
        Validate tenant ID format.
        Must be alphanumeric with hyphens, lowercase.
        """
        if not tenant_id:
            return False

        # Check length (between 3 and 50 characters)
        if not (3 <= len(tenant_id) <= 50):
            return False

        # Check format (lowercase alphanumeric with hyphens)
        if not re.match(r"^[a-z0-9-]+$", tenant_id):
            return False

        # Cannot start or end with hyphen
        if tenant_id.startswith("-") or tenant_id.endswith("-"):
            return False

        return True

    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Process the request and set tenant context.
        """
        # Skip tenant extraction for excluded paths
        if request.url.path in self.EXCLUDED_PATHS:
            # Use default schema
            TenantContext.set_schema(settings.DEFAULT_TENANT_SCHEMA)
            response = await call_next(request)
            TenantContext.clear()
            return response

        # Extract tenant ID
        tenant_id = self._extract_tenant_from_header(
            request
        ) or self._extract_tenant_from_subdomain(request)

        # If no tenant ID found, use default schema
        if not tenant_id:
            logger.warning(
                "no_tenant_id_found",
                path=request.url.path,
                headers=dict(request.headers),
            )
            # For now, allow requests without tenant ID (use default schema)
            # In production, you might want to reject these
            tenant_id = settings.DEFAULT_TENANT_SCHEMA

        # Validate tenant ID
        if (
            not self._validate_tenant_id(tenant_id)
            and tenant_id != settings.DEFAULT_TENANT_SCHEMA
        ):
            logger.error(
                "invalid_tenant_id",
                tenant_id=tenant_id,
                path=request.url.path,
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid tenant ID format: {tenant_id}",
            )

        # Set tenant context
        TenantContext.set_schema(tenant_id)

        # Add tenant ID to request state for easy access
        request.state.tenant_id = tenant_id

        logger.info(
            "tenant_context_set",
            tenant_id=tenant_id,
            path=request.url.path,
        )

        try:
            # Process request
            response = await call_next(request)

            # Add tenant ID to response headers (for debugging)
            response.headers["X-Tenant-ID"] = tenant_id

            return response
        finally:
            # Clear tenant context after request
            TenantContext.clear()

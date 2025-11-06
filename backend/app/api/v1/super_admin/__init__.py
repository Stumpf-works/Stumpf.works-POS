"""
Super Admin API Module
Endpoints only accessible by super admins (Stumpf.works staff)
"""

from fastapi import APIRouter

from app.api.v1.super_admin import plugin_licenses

# Super admin router
router = APIRouter(prefix="/super-admin", tags=["Super Admin"])

# Include sub-routers
router.include_router(plugin_licenses.router)

__all__ = ["router"]

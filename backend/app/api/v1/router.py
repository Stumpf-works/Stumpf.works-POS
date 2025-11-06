"""
API v1 Router
Registers all v1 API endpoints
"""

from fastapi import APIRouter
from app.api.v1 import auth, products, transactions, exports, webhooks, admin, plugins
from app.api.v1 import super_admin

# Create main API router
api_router = APIRouter()

# Include sub-routers
api_router.include_router(auth.router)
api_router.include_router(products.router)
api_router.include_router(transactions.router)
api_router.include_router(exports.router)
api_router.include_router(webhooks.router)
api_router.include_router(admin.router)

# Plugin Management (Tenant Admin)
api_router.include_router(plugins.router)

# Super Admin Routes (Stumpf.works staff only)
api_router.include_router(super_admin.router)

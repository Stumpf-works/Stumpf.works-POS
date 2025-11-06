"""
API v1 Router
Registers all v1 API endpoints
"""

from fastapi import APIRouter
from app.api.v1 import auth, products, transactions, exports, webhooks

# Create main API router
api_router = APIRouter()

# Include sub-routers
api_router.include_router(auth.router)
api_router.include_router(products.router)
api_router.include_router(transactions.router)
api_router.include_router(exports.router)
api_router.include_router(webhooks.router)

# Add more routers as they're created:
# api_router.include_router(users.router)
# etc.

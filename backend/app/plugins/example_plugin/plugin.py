"""
Example Plugin
Demonstrates how to create a plugin for Stumpf.works POS
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.plugins.base import BasePlugin, PluginMetadata, PluginHook
from app.core.database import get_db
from app.api.dependencies import get_current_user

logger = structlog.get_logger()


class ExamplePlugin(BasePlugin):
    """
    Example plugin to demonstrate plugin capabilities.

    This plugin adds a simple endpoint and hooks into transaction events.
    """

    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="Example Plugin",
            version="1.0.0",
            description="A simple example plugin demonstrating the plugin system",
            author="Stumpf.works",
            dependencies=[],
        )

    def get_router(self) -> APIRouter:
        """Add custom API endpoints."""
        router = APIRouter(prefix="/example", tags=["Example Plugin"])

        @router.get("/hello")
        async def hello(current_user=Depends(get_current_user)):
            """Example endpoint that requires authentication."""
            return {
                "message": f"Hello from Example Plugin, {current_user.username}!",
                "plugin": self.metadata.name,
                "version": self.metadata.version,
            }

        @router.get("/info")
        async def info():
            """Get plugin information."""
            return {
                "name": self.metadata.name,
                "version": self.metadata.version,
                "description": self.metadata.description,
                "author": self.metadata.author,
                "enabled": self.enabled,
            }

        return router

    async def on_enable(self):
        """Initialize plugin when enabled."""
        logger.info("example_plugin_enabled")

        # Register hooks
        PluginHook.register("after_transaction_create", self.on_transaction_created)

        # Could initialize external connections, cache, etc.
        logger.info("example_plugin_hooks_registered")

    async def on_disable(self):
        """Cleanup when plugin is disabled."""
        logger.info("example_plugin_disabled")

    async def on_startup(self):
        """Run when application starts."""
        logger.info("example_plugin_startup")

    async def on_shutdown(self):
        """Run when application shuts down."""
        logger.info("example_plugin_shutdown")

    def on_transaction_created(self, transaction, **kwargs):
        """
        Hook that runs after a transaction is created.

        This demonstrates how plugins can react to events.
        """
        logger.info(
            "example_plugin_transaction_hook",
            transaction_id=transaction.id,
            receipt_number=transaction.receipt_number,
            total=transaction.total,
        )

        # Example: Could send notification, update external system, etc.

        return transaction  # Return potentially modified data

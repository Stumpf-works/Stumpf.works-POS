"""
Plugin Base Classes
Define the interface for plugins
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from fastapi import APIRouter


@dataclass
class PluginMetadata:
    """Plugin metadata information."""

    name: str
    version: str
    description: str
    author: str
    dependencies: List[str] = None

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


class BasePlugin(ABC):
    """
    Base class for all plugins.

    Plugins can extend functionality by:
    - Adding API endpoints
    - Adding database models
    - Providing services
    - Registering hooks
    """

    def __init__(self):
        self.metadata = self.get_metadata()
        self.enabled = False

    @abstractmethod
    def get_metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        pass

    def get_router(self) -> Optional[APIRouter]:
        """
        Return FastAPI router with plugin endpoints.

        Override this method to add API endpoints.
        """
        return None

    def get_models(self) -> List[Any]:
        """
        Return list of SQLAlchemy models to register.

        Override this method to add database models.
        """
        return []

    async def on_enable(self):
        """
        Called when plugin is enabled.

        Use this for initialization tasks like:
        - Database setup
        - Service configuration
        - External API connections
        """
        pass

    async def on_disable(self):
        """
        Called when plugin is disabled.

        Use this for cleanup tasks.
        """
        pass

    async def on_startup(self):
        """Called when application starts."""
        pass

    async def on_shutdown(self):
        """Called when application shuts down."""
        pass


class PluginHook:
    """
    Hook system for plugins to intercept events.

    Example hooks:
    - before_transaction_create
    - after_transaction_create
    - before_product_update
    - after_product_update
    """

    _hooks: Dict[str, List[callable]] = {}

    @classmethod
    def register(cls, hook_name: str, callback: callable):
        """Register a callback for a hook."""
        if hook_name not in cls._hooks:
            cls._hooks[hook_name] = []
        cls._hooks[hook_name].append(callback)

    @classmethod
    async def trigger(cls, hook_name: str, *args, **kwargs) -> Any:
        """
        Trigger a hook and execute all registered callbacks.

        Returns the modified data (if applicable).
        """
        if hook_name not in cls._hooks:
            return kwargs.get('data')

        data = kwargs.get('data')

        for callback in cls._hooks[hook_name]:
            result = callback(*args, **kwargs)

            # If callback returns a value, use it as new data
            if result is not None:
                data = result

        return data

    @classmethod
    def list_hooks(cls) -> List[str]:
        """List all registered hooks."""
        return list(cls._hooks.keys())

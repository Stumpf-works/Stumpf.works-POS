"""
Plugin Registry
Manages plugin discovery, loading, and lifecycle
"""

import importlib
import inspect
import os
from pathlib import Path
from typing import Dict, List, Optional

import structlog

from app.plugins.base import BasePlugin

logger = structlog.get_logger()


class PluginRegistry:
    """
    Plugin registry for managing plugins.

    Handles:
    - Plugin discovery
    - Plugin loading
    - Plugin lifecycle
    - Plugin dependencies
    """

    def __init__(self):
        self._plugins: Dict[str, BasePlugin] = {}
        self._enabled_plugins: List[str] = []

    def discover_plugins(self, plugin_dir: str = "app/plugins") -> List[str]:
        """
        Discover plugins in the plugin directory.

        Returns list of discovered plugin names.
        """
        discovered = []

        if not os.path.exists(plugin_dir):
            logger.warning("plugin_directory_not_found", directory=plugin_dir)
            return discovered

        for item in os.listdir(plugin_dir):
            item_path = os.path.join(plugin_dir, item)

            # Skip if not a directory
            if not os.path.isdir(item_path):
                continue

            # Skip special directories
            if item.startswith("_") or item.startswith("."):
                continue

            # Check for plugin.py
            plugin_file = os.path.join(item_path, "plugin.py")
            if not os.path.exists(plugin_file):
                continue

            discovered.append(item)
            logger.info("plugin_discovered", plugin=item)

        return discovered

    def load_plugin(self, plugin_name: str) -> Optional[BasePlugin]:
        """
        Load a plugin by name.

        Imports the plugin module and instantiates the plugin class.
        """
        try:
            # Import plugin module
            module_path = f"app.plugins.{plugin_name}.plugin"
            module = importlib.import_module(module_path)

            # Find plugin class (must inherit from BasePlugin)
            plugin_class = None
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, BasePlugin) and obj is not BasePlugin:
                    plugin_class = obj
                    break

            if not plugin_class:
                logger.error("no_plugin_class_found", plugin=plugin_name)
                return None

            # Instantiate plugin
            plugin = plugin_class()
            self._plugins[plugin_name] = plugin

            logger.info(
                "plugin_loaded",
                plugin=plugin_name,
                version=plugin.metadata.version,
            )

            return plugin

        except Exception as e:
            logger.exception("plugin_load_error", plugin=plugin_name, error=str(e))
            return None

    async def enable_plugin(self, plugin_name: str) -> bool:
        """
        Enable a plugin.

        Calls the plugin's on_enable() method.
        """
        if plugin_name not in self._plugins:
            plugin = self.load_plugin(plugin_name)
            if not plugin:
                return False

        plugin = self._plugins[plugin_name]

        if plugin.enabled:
            logger.warning("plugin_already_enabled", plugin=plugin_name)
            return True

        try:
            await plugin.on_enable()
            plugin.enabled = True
            self._enabled_plugins.append(plugin_name)

            logger.info("plugin_enabled", plugin=plugin_name)
            return True

        except Exception as e:
            logger.exception("plugin_enable_error", plugin=plugin_name, error=str(e))
            return False

    async def disable_plugin(self, plugin_name: str) -> bool:
        """
        Disable a plugin.

        Calls the plugin's on_disable() method.
        """
        if plugin_name not in self._plugins:
            logger.error("plugin_not_found", plugin=plugin_name)
            return False

        plugin = self._plugins[plugin_name]

        if not plugin.enabled:
            logger.warning("plugin_not_enabled", plugin=plugin_name)
            return True

        try:
            await plugin.on_disable()
            plugin.enabled = False
            self._enabled_plugins.remove(plugin_name)

            logger.info("plugin_disabled", plugin=plugin_name)
            return True

        except Exception as e:
            logger.exception("plugin_disable_error", plugin=plugin_name, error=str(e))
            return False

    def get_plugin(self, plugin_name: str) -> Optional[BasePlugin]:
        """Get a plugin by name."""
        return self._plugins.get(plugin_name)

    def get_enabled_plugins(self) -> List[BasePlugin]:
        """Get list of enabled plugins."""
        return [
            self._plugins[name]
            for name in self._enabled_plugins
            if name in self._plugins
        ]

    def get_all_plugins(self) -> List[BasePlugin]:
        """Get list of all loaded plugins."""
        return list(self._plugins.values())

    async def startup_plugins(self):
        """Call on_startup() for all enabled plugins."""
        for plugin_name in self._enabled_plugins:
            if plugin_name in self._plugins:
                try:
                    await self._plugins[plugin_name].on_startup()
                    logger.info("plugin_started", plugin=plugin_name)
                except Exception as e:
                    logger.exception(
                        "plugin_startup_error", plugin=plugin_name, error=str(e)
                    )

    async def shutdown_plugins(self):
        """Call on_shutdown() for all enabled plugins."""
        for plugin_name in self._enabled_plugins:
            if plugin_name in self._plugins:
                try:
                    await self._plugins[plugin_name].on_shutdown()
                    logger.info("plugin_shutdown", plugin=plugin_name)
                except Exception as e:
                    logger.exception(
                        "plugin_shutdown_error", plugin=plugin_name, error=str(e)
                    )


# Global plugin registry instance
plugin_registry = PluginRegistry()

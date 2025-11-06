"""
Plugin System
Extensibility framework for Stumpf.works POS
"""

from app.plugins.base import BasePlugin, PluginMetadata, PluginHook
from app.plugins.registry import PluginRegistry, plugin_registry

__all__ = [
    "BasePlugin",
    "PluginMetadata",
    "PluginHook",
    "PluginRegistry",
    "plugin_registry",
]

"""
Plugin Management API (Tenant Admin)
Allows tenant admins to manage LICENSED plugins for their tenant
"""

from typing import List, Optional

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db, require_admin
from app.models.plugin_license import PluginLicense
from app.models.user import User
from app.plugins import plugin_registry

logger = structlog.get_logger()
router = APIRouter(prefix="/plugins", tags=["Plugins"])


class PluginInfo(BaseModel):
    """Plugin information response."""

    name: str
    display_name: str
    description: str
    version: str
    author: Optional[str] = None
    category: str  # "restaurant", "retail", "general", etc.
    is_enabled: bool
    is_loaded: bool
    requires: List[str] = []  # Required plugins
    config_schema: Optional[dict] = None
    # License info
    is_licensed: bool
    license_type: Optional[str] = None  # standard, trial, enterprise
    license_valid: bool = False
    license_expires: Optional[str] = None
    days_remaining: Optional[int] = None


class PluginConfig(BaseModel):
    """Plugin configuration."""

    enabled: bool
    config: Optional[dict] = None


class PluginEnableRequest(BaseModel):
    """Request to enable a plugin."""

    config: Optional[dict] = None


# Helper Functions


async def get_plugin_license(
    db: AsyncSession, tenant_id: str, plugin_name: str
) -> Optional[PluginLicense]:
    """Get plugin license for tenant."""
    result = await db.execute(
        select(PluginLicense).where(
            PluginLicense.tenant_id == tenant_id,
            PluginLicense.plugin_name == plugin_name,
        )
    )
    return result.scalar_one_or_none()


async def check_plugin_licensed(
    db: AsyncSession, tenant_id: str, plugin_name: str
) -> tuple[bool, Optional[PluginLicense]]:
    """Check if plugin is licensed and valid for tenant."""
    license = await get_plugin_license(db, tenant_id, plugin_name)
    if not license:
        return False, None
    return license.is_valid, license


@router.get("", response_model=List[PluginInfo])
async def list_plugins(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    List all LICENSED plugins for the tenant.

    Only shows plugins that the tenant has a valid license for.
    """
    plugins_info = []

    # Get all licenses for this tenant
    result = await db.execute(
        select(PluginLicense).where(PluginLicense.tenant_id == current_user.tenant_id)
    )
    licenses = result.scalars().all()

    for license in licenses:
        plugin_name = license.plugin_name
        plugin = plugin_registry.get_plugin(plugin_name)

        if plugin:
            # Plugin is loaded
            plugins_info.append(
                PluginInfo(
                    name=plugin_name,
                    display_name=(
                        plugin.get_display_name()
                        if hasattr(plugin, "get_display_name")
                        else plugin_name
                    ),
                    description=(
                        plugin.get_description()
                        if hasattr(plugin, "get_description")
                        else "No description"
                    ),
                    version=plugin.get_version(),
                    author=(
                        plugin.get_author() if hasattr(plugin, "get_author") else None
                    ),
                    category=(
                        plugin.get_category()
                        if hasattr(plugin, "get_category")
                        else "general"
                    ),
                    is_enabled=plugin_registry.is_enabled(plugin_name),
                    is_loaded=True,
                    requires=(
                        plugin.get_requires() if hasattr(plugin, "get_requires") else []
                    ),
                    config_schema=(
                        plugin.get_config_schema()
                        if hasattr(plugin, "get_config_schema")
                        else None
                    ),
                    is_licensed=True,
                    license_type=license.license_type,
                    license_valid=license.is_valid,
                    license_expires=(
                        license.valid_until.isoformat() if license.valid_until else None
                    ),
                    days_remaining=license.days_remaining,
                )
            )
        else:
            # Plugin is licensed but not loaded yet
            plugins_info.append(
                PluginInfo(
                    name=plugin_name,
                    display_name=plugin_name,
                    description="Plugin not loaded",
                    version="unknown",
                    category="general",
                    is_enabled=False,
                    is_loaded=False,
                    is_licensed=True,
                    license_type=license.license_type,
                    license_valid=license.is_valid,
                    license_expires=(
                        license.valid_until.isoformat() if license.valid_until else None
                    ),
                    days_remaining=license.days_remaining,
                )
            )

    logger.info(
        "plugins_listed",
        user_id=current_user.id,
        tenant_id=current_user.tenant_id,
        count=len(plugins_info),
    )

    return plugins_info


@router.get("/{plugin_name}", response_model=PluginInfo)
async def get_plugin_info(
    plugin_name: str,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Get detailed information about a specific plugin.

    Only shows plugins that the tenant has a valid license for.
    """
    # Check license
    is_licensed, license = await check_plugin_licensed(
        db, current_user.tenant_id, plugin_name
    )
    if not is_licensed or not license:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                f"No valid license for plugin '{plugin_name}'. "
                "Contact Stumpf.works to obtain a license."
            ),
        )

    plugin = plugin_registry.get_plugin(plugin_name)

    if not plugin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plugin '{plugin_name}' not found or not loaded",
        )

    return PluginInfo(
        name=plugin_name,
        display_name=(
            plugin.get_display_name()
            if hasattr(plugin, "get_display_name")
            else plugin_name
        ),
        description=(
            plugin.get_description()
            if hasattr(plugin, "get_description")
            else "No description"
        ),
        version=plugin.get_version(),
        author=plugin.get_author() if hasattr(plugin, "get_author") else None,
        category=(
            plugin.get_category() if hasattr(plugin, "get_category") else "general"
        ),
        is_enabled=plugin_registry.is_enabled(plugin_name),
        is_loaded=True,
        requires=plugin.get_requires() if hasattr(plugin, "get_requires") else [],
        config_schema=(
            plugin.get_config_schema() if hasattr(plugin, "get_config_schema") else None
        ),
        is_licensed=True,
        license_type=license.license_type,
        license_valid=license.is_valid,
        license_expires=(
            license.valid_until.isoformat() if license.valid_until else None
        ),
        days_remaining=license.days_remaining,
    )


@router.post("/{plugin_name}/enable")
async def enable_plugin(
    plugin_name: str,
    request: PluginEnableRequest,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Enable a plugin for the current tenant.

    Requires a valid license for the plugin.

    This will:
    1. Verify license
    2. Load the plugin if not loaded
    3. Initialize it with provided config
    4. Enable it for this tenant
    """
    try:
        # CHECK LICENSE FIRST
        is_licensed, license = await check_plugin_licensed(
            db, current_user.tenant_id, plugin_name
        )
        if not is_licensed or not license:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"No valid license for plugin '{plugin_name}'. "
                    "Contact Stumpf.works support to obtain a license."
                ),
            )

        # Show trial warning
        if license.is_trial and license.days_remaining:
            logger.warning(
                "trial_plugin_enabled",
                plugin=plugin_name,
                tenant=current_user.tenant_id,
                days_remaining=license.days_remaining,
            )

        # Check if plugin exists
        if plugin_name not in plugin_registry.discover_plugins():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Plugin '{plugin_name}' not found",
            )

        # Load plugin if not loaded
        plugin = plugin_registry.get_plugin(plugin_name)
        if not plugin:
            plugin = plugin_registry.load_plugin(plugin_name)
            if not plugin:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to load plugin '{plugin_name}'",
                )

        # Check dependencies
        if hasattr(plugin, "get_requires"):
            required = plugin.get_requires()
            for req_plugin in required:
                if not plugin_registry.is_enabled(req_plugin):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=(
                            f"Plugin '{plugin_name}' requires "
                            f"'{req_plugin}' to be enabled first"
                        ),
                    )

        # Configure plugin if config provided
        if request.config and hasattr(plugin, "configure"):
            plugin.configure(request.config)

        # Enable plugin
        await plugin_registry.enable_plugin(plugin_name)

        logger.info(
            "plugin_enabled",
            plugin=plugin_name,
            user_id=current_user.id,
            tenant_id=current_user.tenant_id,
        )

        return {
            "message": f"Plugin '{plugin_name}' enabled successfully",
            "plugin": plugin_name,
            "status": "enabled",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "plugin_enable_failed", plugin=plugin_name, error=str(e), exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to enable plugin: {str(e)}",
        )


@router.post("/{plugin_name}/disable")
async def disable_plugin(
    plugin_name: str,
    current_user: User = Depends(require_admin),
):
    """
    Disable a plugin for the current tenant.

    This will:
    1. Disable the plugin
    2. Stop any background tasks
    3. Unregister routes (requires restart)
    """
    try:
        # Check if plugin is loaded
        plugin = plugin_registry.get_plugin(plugin_name)
        if not plugin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Plugin '{plugin_name}' not found or not loaded",
            )

        # Check if other plugins depend on this one
        dependencies = []
        for other_plugin_name in plugin_registry.discover_plugins():
            other_plugin = plugin_registry.get_plugin(other_plugin_name)
            if other_plugin and hasattr(other_plugin, "get_requires"):
                if plugin_name in other_plugin.get_requires():
                    if plugin_registry.is_enabled(other_plugin_name):
                        dependencies.append(other_plugin_name)

        if dependencies:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot disable '{plugin_name}'. Required by: {', '.join(dependencies)}",
            )

        # Disable plugin
        await plugin_registry.disable_plugin(plugin_name)

        logger.info(
            "plugin_disabled",
            plugin=plugin_name,
            user_id=current_user.id,
            tenant_id=current_user.tenant_id,
        )

        return {
            "message": f"Plugin '{plugin_name}' disabled successfully",
            "plugin": plugin_name,
            "status": "disabled",
            "note": "Application restart may be required for full effect",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "plugin_disable_failed", plugin=plugin_name, error=str(e), exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to disable plugin: {str(e)}",
        )


@router.patch("/{plugin_name}/config")
async def update_plugin_config(
    plugin_name: str,
    config: dict,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Update configuration for a plugin.

    Requires a valid license for the plugin.
    """
    # Check license
    is_licensed, license = await check_plugin_licensed(
        db, current_user.tenant_id, plugin_name
    )
    if not is_licensed or not license:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"No valid license for plugin '{plugin_name}'. Contact Stumpf.works support.",
        )

    plugin = plugin_registry.get_plugin(plugin_name)

    if not plugin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plugin '{plugin_name}' not found",
        )

    if not hasattr(plugin, "configure"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Plugin '{plugin_name}' does not support configuration",
        )

    try:
        plugin.configure(config)

        logger.info(
            "plugin_configured",
            plugin=plugin_name,
            user_id=current_user.id,
        )

        return {
            "message": f"Plugin '{plugin_name}' configured successfully",
            "config": config,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid configuration: {str(e)}",
        )


@router.get("/categories/available")
async def get_plugin_categories(
    current_user: User = Depends(require_admin),
):
    """
    Get available plugin categories.

    Useful for filtering plugins by use case.
    """
    categories = {
        "restaurant": {
            "name": "Restaurant",
            "description": "Plugins for restaurant and gastronomy",
            "icon": "🍽️",
        },
        "retail": {
            "name": "Einzelhandel",
            "description": "Plugins for retail stores",
            "icon": "🛒",
        },
        "pharmacy": {
            "name": "Apotheke",
            "description": "Plugins for pharmacies",
            "icon": "💊",
        },
        "bakery": {
            "name": "Bäckerei",
            "description": "Plugins for bakeries",
            "icon": "🥖",
        },
        "general": {
            "name": "Allgemein",
            "description": "General purpose plugins",
            "icon": "⚙️",
        },
        "hardware": {
            "name": "Hardware",
            "description": "Hardware integration plugins",
            "icon": "🖨️",
        },
        "payment": {
            "name": "Zahlung",
            "description": "Payment provider plugins",
            "icon": "💳",
        },
        "analytics": {
            "name": "Analytics",
            "description": "Analytics and reporting plugins",
            "icon": "📊",
        },
    }

    return categories

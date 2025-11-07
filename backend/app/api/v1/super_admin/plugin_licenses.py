"""
Super Admin Plugin License Management API
Only accessible by super admins to grant/revoke plugin licenses to tenants
"""

from datetime import datetime, timedelta
from typing import List, Optional

import structlog
from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_db
from app.models.plugin_license import PluginLicense
from app.models.tenant import Tenant
from app.models.user import User, UserRole
from app.plugins import plugin_registry

logger = structlog.get_logger()
router = APIRouter(prefix="/plugin-licenses", tags=["Super Admin - Plugin Licenses"])


# Dependency to require super admin
async def require_super_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require user to be super admin."""
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Super admin access required"
        )
    return current_user


# Request/Response Models


class PluginLicenseCreate(BaseModel):
    """Request to grant a plugin license."""

    tenant_id: str
    plugin_name: str
    license_type: str = "standard"  # standard, trial, enterprise
    valid_days: Optional[int] = None  # NULL = unlimited
    max_users: Optional[int] = None
    max_locations: Optional[int] = None
    notes: Optional[str] = None


class PluginLicenseUpdate(BaseModel):
    """Request to update a plugin license."""

    is_active: Optional[bool] = None
    license_type: Optional[str] = None
    valid_until: Optional[datetime] = None
    max_users: Optional[int] = None
    max_locations: Optional[int] = None
    notes: Optional[str] = None


class PluginLicenseInfo(BaseModel):
    """Plugin license information response."""

    id: int
    tenant_id: str
    tenant_name: str
    plugin_name: str
    plugin_display_name: str
    is_active: bool
    is_valid: bool
    license_type: str
    valid_from: datetime
    valid_until: Optional[datetime]
    days_remaining: Optional[int]
    max_users: Optional[int]
    max_locations: Optional[int]
    notes: Optional[str]
    granted_at: datetime
    created_at: datetime


class TenantWithLicenses(BaseModel):
    """Tenant with their plugin licenses."""

    tenant_id: str
    tenant_name: str
    active_licenses: int
    total_licenses: int
    plugins: List[str]


# Endpoints


@router.get("/tenants", response_model=List[TenantWithLicenses])
async def list_tenants_with_licenses(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_super_admin),
):
    """
    List all tenants with their plugin license summary.

    Useful for overview of which tenants have which plugins.
    """
    # Get all tenants
    result = await db.execute(select(Tenant))
    tenants = result.scalars().all()

    tenant_data = []
    for tenant in tenants:
        # Count licenses
        license_result = await db.execute(
            select(PluginLicense).where(PluginLicense.tenant_id == tenant.slug)
        )
        licenses = license_result.scalars().all()

        active_licenses = [lic for lic in licenses if lic.is_valid]

        tenant_data.append(
            TenantWithLicenses(
                tenant_id=tenant.slug,
                tenant_name=tenant.name,
                active_licenses=len(active_licenses),
                total_licenses=len(licenses),
                plugins=[lic.plugin_name for lic in active_licenses],
            )
        )

    logger.info(
        "tenants_with_licenses_listed", user_id=current_user.id, count=len(tenant_data)
    )

    return tenant_data


@router.get("", response_model=List[PluginLicenseInfo])
async def list_plugin_licenses(
    tenant_id: Optional[str] = Query(None, description="Filter by tenant"),
    plugin_name: Optional[str] = Query(None, description="Filter by plugin"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_super_admin),
):
    """
    List all plugin licenses with filters.

    Super admins can see all licenses across all tenants.
    """
    query = select(PluginLicense)

    # Apply filters
    if tenant_id:
        query = query.where(PluginLicense.tenant_id == tenant_id)
    if plugin_name:
        query = query.where(PluginLicense.plugin_name == plugin_name)
    if is_active is not None:
        query = query.where(PluginLicense.is_active == is_active)

    result = await db.execute(query)
    licenses = result.scalars().all()

    # Enrich with tenant and plugin info
    licenses_info = []
    for lic in licenses:
        # Get tenant name
        tenant_result = await db.execute(
            select(Tenant).where(Tenant.slug == lic.tenant_id)
        )
        tenant = tenant_result.scalar_one_or_none()
        tenant_name = tenant.name if tenant else lic.tenant_id

        # Get plugin display name
        plugin = plugin_registry.get_plugin(lic.plugin_name)
        plugin_display_name = (
            plugin.get_display_name()
            if plugin and hasattr(plugin, "get_display_name")
            else lic.plugin_name
        )

        licenses_info.append(
            PluginLicenseInfo(
                id=lic.id,
                tenant_id=lic.tenant_id,
                tenant_name=tenant_name,
                plugin_name=lic.plugin_name,
                plugin_display_name=plugin_display_name,
                is_active=lic.is_active,
                is_valid=lic.is_valid,
                license_type=lic.license_type,
                valid_from=lic.valid_from,
                valid_until=lic.valid_until,
                days_remaining=lic.days_remaining,
                max_users=lic.max_users,
                max_locations=lic.max_locations,
                notes=lic.notes,
                granted_at=lic.granted_at,
                created_at=lic.created_at,
            )
        )

    logger.info(
        "plugin_licenses_listed",
        user_id=current_user.id,
        count=len(licenses_info),
        filters={"tenant_id": tenant_id, "plugin_name": plugin_name},
    )

    return licenses_info


@router.post("", response_model=PluginLicenseInfo, status_code=status.HTTP_201_CREATED)
async def grant_plugin_license(
    request: PluginLicenseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_super_admin),
):
    """
    Grant a plugin license to a tenant.

    This allows the tenant admin to enable and configure the plugin.
    """
    # Verify tenant exists
    tenant_result = await db.execute(
        select(Tenant).where(Tenant.slug == request.tenant_id)
    )
    tenant = tenant_result.scalar_one_or_none()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tenant '{request.tenant_id}' not found",
        )

    # Verify plugin exists
    if request.plugin_name not in plugin_registry.discover_plugins():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plugin '{request.plugin_name}' not found",
        )

    # Check if license already exists
    existing_result = await db.execute(
        select(PluginLicense).where(
            PluginLicense.tenant_id == request.tenant_id,
            PluginLicense.plugin_name == request.plugin_name,
        )
    )
    existing = existing_result.scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"License already exists for '{request.plugin_name}' "
                f"(ID: {existing.id}). Use PATCH to update."
            ),
        )

    # Calculate valid_until
    valid_until = None
    if request.valid_days:
        valid_until = datetime.utcnow() + timedelta(days=request.valid_days)

    # Create license
    license = PluginLicense(
        tenant_id=request.tenant_id,
        plugin_name=request.plugin_name,
        is_active=True,
        license_type=request.license_type,
        valid_from=datetime.utcnow(),
        valid_until=valid_until,
        max_users=request.max_users,
        max_locations=request.max_locations,
        notes=request.notes,
        granted_by=current_user.id,
        granted_at=datetime.utcnow(),
    )

    db.add(license)
    await db.commit()
    await db.refresh(license)

    # Get plugin display name
    plugin = plugin_registry.get_plugin(request.plugin_name)
    plugin_display_name = (
        plugin.get_display_name()
        if plugin and hasattr(plugin, "get_display_name")
        else request.plugin_name
    )

    logger.info(
        "plugin_license_granted",
        license_id=license.id,
        tenant_id=request.tenant_id,
        plugin=request.plugin_name,
        license_type=request.license_type,
        granted_by=current_user.id,
    )

    return PluginLicenseInfo(
        id=license.id,
        tenant_id=license.tenant_id,
        tenant_name=tenant.name,
        plugin_name=license.plugin_name,
        plugin_display_name=plugin_display_name,
        is_active=license.is_active,
        is_valid=license.is_valid,
        license_type=license.license_type,
        valid_from=license.valid_from,
        valid_until=license.valid_until,
        days_remaining=license.days_remaining,
        max_users=license.max_users,
        max_locations=license.max_locations,
        notes=license.notes,
        granted_at=license.granted_at,
        created_at=license.created_at,
    )


@router.patch("/{license_id}", response_model=PluginLicenseInfo)
async def update_plugin_license(
    license_id: int,
    request: PluginLicenseUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_super_admin),
):
    """
    Update a plugin license.

    Can be used to extend validity, change license type, activate/deactivate, etc.
    """
    # Get license
    result = await db.execute(
        select(PluginLicense).where(PluginLicense.id == license_id)
    )
    license = result.scalar_one_or_none()
    if not license:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"License {license_id} not found",
        )

    # Update fields
    if request.is_active is not None:
        license.is_active = request.is_active
    if request.license_type:
        license.license_type = request.license_type
    if request.valid_until is not None:
        license.valid_until = request.valid_until
    if request.max_users is not None:
        license.max_users = request.max_users
    if request.max_locations is not None:
        license.max_locations = request.max_locations
    if request.notes is not None:
        license.notes = request.notes

    await db.commit()
    await db.refresh(license)

    # Get tenant name
    tenant_result = await db.execute(
        select(Tenant).where(Tenant.slug == license.tenant_id)
    )
    tenant = tenant_result.scalar_one_or_none()
    tenant_name = tenant.name if tenant else license.tenant_id

    # Get plugin display name
    plugin = plugin_registry.get_plugin(license.plugin_name)
    plugin_display_name = (
        plugin.get_display_name()
        if plugin and hasattr(plugin, "get_display_name")
        else license.plugin_name
    )

    logger.info(
        "plugin_license_updated",
        license_id=license_id,
        updated_by=current_user.id,
        changes=request.dict(exclude_unset=True),
    )

    return PluginLicenseInfo(
        id=license.id,
        tenant_id=license.tenant_id,
        tenant_name=tenant_name,
        plugin_name=license.plugin_name,
        plugin_display_name=plugin_display_name,
        is_active=license.is_active,
        is_valid=license.is_valid,
        license_type=license.license_type,
        valid_from=license.valid_from,
        valid_until=license.valid_until,
        days_remaining=license.days_remaining,
        max_users=license.max_users,
        max_locations=license.max_locations,
        notes=license.notes,
        granted_at=license.granted_at,
        created_at=license.created_at,
    )


@router.delete("/{license_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_plugin_license(
    license_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_super_admin),
):
    """
    Revoke (delete) a plugin license.

    This will prevent the tenant from using the plugin.
    The plugin will be automatically disabled if currently enabled.
    """
    # Get license
    result = await db.execute(
        select(PluginLicense).where(PluginLicense.id == license_id)
    )
    license = result.scalar_one_or_none()
    if not license:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"License {license_id} not found",
        )

    tenant_id = license.tenant_id
    plugin_name = license.plugin_name

    # Delete license
    await db.delete(license)
    await db.commit()

    # Disable plugin if currently enabled
    if plugin_registry.is_enabled(plugin_name):
        try:
            await plugin_registry.disable_plugin(plugin_name)
        except Exception as e:
            logger.warning(
                "failed_to_disable_plugin_after_license_revoke",
                plugin=plugin_name,
                error=str(e),
            )

    logger.info(
        "plugin_license_revoked",
        license_id=license_id,
        tenant_id=tenant_id,
        plugin=plugin_name,
        revoked_by=current_user.id,
    )

    return None


@router.post("/{license_id}/extend")
async def extend_plugin_license(
    license_id: int,
    days: int = Body(..., gt=0, description="Number of days to extend"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_super_admin),
):
    """
    Extend a plugin license validity by specified days.
    """
    # Get license
    result = await db.execute(
        select(PluginLicense).where(PluginLicense.id == license_id)
    )
    license = result.scalar_one_or_none()
    if not license:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"License {license_id} not found",
        )

    # Extend
    if license.valid_until:
        license.valid_until = license.valid_until + timedelta(days=days)
    else:
        # If unlimited, set expiry from now
        license.valid_until = datetime.utcnow() + timedelta(days=days)

    await db.commit()
    await db.refresh(license)

    logger.info(
        "plugin_license_extended",
        license_id=license_id,
        days=days,
        new_expiry=license.valid_until,
        extended_by=current_user.id,
    )

    return {
        "message": f"License extended by {days} days",
        "license_id": license_id,
        "valid_until": license.valid_until,
        "days_remaining": license.days_remaining,
    }

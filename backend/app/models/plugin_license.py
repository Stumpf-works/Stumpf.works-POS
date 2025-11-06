"""
Plugin License Model
Tracks which plugins are licensed to which tenants
"""

from sqlalchemy import Column, String, Boolean, DateTime, Text, JSON, Integer
from datetime import datetime, timedelta
from typing import Optional

from app.models.base import BaseModel


class PluginLicense(BaseModel):
    """
    Plugin License model.

    Tracks which plugins are available to which tenants.
    Super admins grant licenses, tenant admins can only enable licensed plugins.
    """

    __tablename__ = "plugin_licenses"

    # Tenant this license is for
    tenant_id = Column(String(100), nullable=False, index=True)

    # Plugin identifier
    plugin_name = Column(String(100), nullable=False, index=True)

    # License status
    is_active = Column(Boolean, default=True, nullable=False)

    # License validity
    valid_from = Column(DateTime, default=datetime.utcnow, nullable=False)
    valid_until = Column(DateTime, nullable=True)  # NULL = unlimited

    # License metadata
    license_type = Column(String(50), default="standard")  # standard, trial, enterprise
    max_users = Column(Integer, nullable=True)  # NULL = unlimited
    max_locations = Column(Integer, nullable=True)  # NULL = unlimited

    # Additional configuration/restrictions
    config = Column(JSON, nullable=True)
    notes = Column(Text, nullable=True)

    # Audit trail
    granted_by = Column(Integer, nullable=True)  # Super admin user ID who granted
    granted_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<PluginLicense(tenant={self.tenant_id}, plugin={self.plugin_name}, active={self.is_active})>"

    @property
    def is_valid(self) -> bool:
        """Check if license is currently valid."""
        if not self.is_active:
            return False

        now = datetime.utcnow()

        # Check valid_from
        if self.valid_from and now < self.valid_from:
            return False

        # Check valid_until
        if self.valid_until and now > self.valid_until:
            return False

        return True

    @property
    def is_trial(self) -> bool:
        """Check if this is a trial license."""
        return self.license_type == "trial"

    @property
    def days_remaining(self) -> Optional[int]:
        """Get days remaining on license."""
        if not self.valid_until:
            return None

        delta = self.valid_until - datetime.utcnow()
        return max(0, delta.days)

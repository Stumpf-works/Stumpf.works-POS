"""
Tenant Model
Represents a customer/organization using the POS system
"""

import enum

from sqlalchemy import JSON, Boolean, Column
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import String
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class TenantStatus(str, enum.Enum):
    """Tenant status enumeration."""

    ACTIVE = "active"
    SUSPENDED = "suspended"
    TRIAL = "trial"
    INACTIVE = "inactive"


class Tenant(BaseModel):
    """
    Tenant model for multi-tenancy.

    Each tenant represents a separate customer/organization with:
    - Isolated database schema
    - Own users and data
    - Separate API keys for integrations
    """

    __tablename__ = "tenants"

    # Basic Information
    name = Column(String(100), nullable=False)
    slug = Column(String(50), unique=True, nullable=False, index=True)
    schema_name = Column(String(50), unique=True, nullable=False, index=True)

    # Contact Information
    email = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=True)

    # Address
    address_street = Column(String(255), nullable=True)
    address_city = Column(String(100), nullable=True)
    address_postal_code = Column(String(20), nullable=True)
    address_country = Column(
        String(2), default="DE", nullable=False
    )  # ISO 3166-1 alpha-2

    # Tax Information
    vat_id = Column(String(50), nullable=True)  # USt-IdNr
    tax_number = Column(String(50), nullable=True)  # Steuernummer

    # Status
    status = Column(SQLEnum(TenantStatus), default=TenantStatus.TRIAL, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Integration Settings (encrypted in production)
    settings = Column(JSON, default={}, nullable=False)
    # Example settings structure:
    # {
    #     "sumup": {
    #         "client_id": "...",
    #         "client_secret": "...",
    #         "merchant_code": "..."
    #     },
    #     "fiskaly": {
    #         "api_key": "...",
    #         "api_secret": "...",
    #         "tss_id": "..."
    #     },
    #     "locale": "de_DE",
    #     "currency": "EUR",
    #     "timezone": "Europe/Berlin"
    # }

    # Relationships (to be added)
    # users = relationship("User", back_populates="tenant")
    # locations = relationship("Location", back_populates="tenant")

    def __repr__(self) -> str:
        return f"<Tenant(id={self.id}, slug={self.slug}, name={self.name})>"

    @property
    def is_trial(self) -> bool:
        """Check if tenant is in trial period."""
        return self.status == TenantStatus.TRIAL

    @property
    def can_access(self) -> bool:
        """Check if tenant can access the system."""
        return self.is_active and self.status in [
            TenantStatus.ACTIVE,
            TenantStatus.TRIAL,
        ]

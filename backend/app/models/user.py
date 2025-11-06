"""
User Model
Represents users with tenant-scoped access
"""

from sqlalchemy import Column, String, Boolean, Enum as SQLEnum, ForeignKey, Integer, Table
from sqlalchemy.orm import relationship
import enum

from app.models.base import BaseModel, TenantMixin


class UserRole(str, enum.Enum):
    """User role enumeration."""

    SUPER_ADMIN = "super_admin"  # Platform admin (cross-tenant)
    TENANT_ADMIN = "tenant_admin"  # Tenant administrator
    MANAGER = "manager"  # Store manager
    CASHIER = "cashier"  # POS operator
    VIEWER = "viewer"  # Read-only access


class User(BaseModel, TenantMixin):
    """
    User model for authentication and authorization.

    Users are scoped to a tenant (multi-tenant setup).
    Each user can have different roles and permissions.
    """

    __tablename__ = "users"

    # Basic Information
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)

    # Personal Information
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)

    # Role & Status
    role = Column(SQLEnum(UserRole), default=UserRole.CASHIER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)

    # PIN for quick POS login (4-6 digits)
    pin_code = Column(String(6), nullable=True)

    # Relationships
    # transactions = relationship("Transaction", back_populates="user")
    # shifts = relationship("CashierShift", back_populates="user")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"

    @property
    def full_name(self) -> str:
        """Get full name of user."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username

    @property
    def is_admin(self) -> bool:
        """Check if user is an admin."""
        return self.role in [UserRole.SUPER_ADMIN, UserRole.TENANT_ADMIN]

    @property
    def is_cashier(self) -> bool:
        """Check if user is a cashier."""
        return self.role == UserRole.CASHIER

    @property
    def can_access_pos(self) -> bool:
        """Check if user can access POS terminal."""
        return self.role in [UserRole.CASHIER, UserRole.MANAGER, UserRole.TENANT_ADMIN]

"""
Base model classes for SQLAlchemy models
Includes common fields and mixins
"""

from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, String
from sqlalchemy.ext.declarative import declared_attr

from app.core.database import Base


class TimestampMixin:
    """Mixin to add created_at and updated_at timestamps."""

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )


class TenantMixin:
    """Mixin to add tenant_id to models (optional, for reference)."""

    tenant_id = Column(String(50), nullable=False, index=True)


class BaseModel(Base, TimestampMixin):
    """
    Base model class for all database models.
    Includes primary key and timestamps.
    """

    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    @declared_attr
    def __tablename__(cls) -> str:
        """Generate table name from class name."""
        return cls.__name__.lower()

    def __repr__(self) -> str:
        """String representation of model."""
        return f"<{self.__class__.__name__}(id={self.id})>"

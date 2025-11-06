"""
User Schemas
Pydantic schemas for user-related API requests/responses
"""

from typing import Optional
from pydantic import EmailStr, Field, field_validator
from app.schemas.base import BaseSchema, BaseResponse
from app.models.user import UserRole


class UserBase(BaseSchema):
    """Base user schema with common fields."""

    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    role: UserRole = UserRole.CASHIER


class UserCreate(UserBase):
    """Schema for creating a new user."""

    password: str = Field(..., min_length=8, max_length=100)
    pin_code: Optional[str] = Field(None, min_length=4, max_length=6)

    @field_validator("pin_code")
    @classmethod
    def validate_pin(cls, v):
        """Validate PIN code is numeric."""
        if v and not v.isdigit():
            raise ValueError("PIN code must be numeric")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserUpdate(BaseSchema):
    """Schema for updating a user."""

    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    pin_code: Optional[str] = Field(None, min_length=4, max_length=6)


class UserResponse(BaseResponse):
    """Schema for user response."""

    email: str
    username: str
    first_name: Optional[str]
    last_name: Optional[str]
    role: UserRole
    is_active: bool
    is_verified: bool
    tenant_id: str

    @property
    def full_name(self) -> str:
        """Get full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username


class UserLogin(BaseSchema):
    """Schema for user login."""

    username_or_email: str
    password: str


class UserPINLogin(BaseSchema):
    """Schema for PIN-based login (quick POS login)."""

    pin_code: str = Field(..., min_length=4, max_length=6)


class PasswordChange(BaseSchema):
    """Schema for changing password."""

    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v):
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v

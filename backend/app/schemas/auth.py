"""
Authentication Schemas
Pydantic schemas for authentication-related API requests/responses
"""

from typing import Optional
from pydantic import Field
from app.schemas.base import BaseSchema


class Token(BaseSchema):
    """Token response schema."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseSchema):
    """JWT token payload schema."""

    sub: str  # User ID
    tenant_id: str
    exp: int  # Expiration timestamp
    type: str  # 'access' or 'refresh'


class RefreshTokenRequest(BaseSchema):
    """Refresh token request schema."""

    refresh_token: str


class TokenVerifyResponse(BaseSchema):
    """Token verification response."""

    valid: bool
    user_id: Optional[int] = None
    tenant_id: Optional[str] = None
    expires_at: Optional[int] = None

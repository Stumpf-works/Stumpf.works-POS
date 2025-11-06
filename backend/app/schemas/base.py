"""
Base Pydantic schemas for API requests/responses
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel as PydanticBaseModel, ConfigDict


class BaseSchema(PydanticBaseModel):
    """Base schema with common configuration."""

    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        arbitrary_types_allowed=True,
    )


class TimestampSchema(BaseSchema):
    """Schema mixin for timestamps."""

    created_at: datetime
    updated_at: datetime


class IDSchema(BaseSchema):
    """Schema mixin for ID."""

    id: int


class BaseResponse(IDSchema, TimestampSchema):
    """Base response schema with ID and timestamps."""

    pass


class ErrorResponse(BaseSchema):
    """Standard error response."""

    detail: str
    code: Optional[str] = None


class MessageResponse(BaseSchema):
    """Simple message response."""

    message: str
    success: bool = True

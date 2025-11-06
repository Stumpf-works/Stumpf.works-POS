"""
Product Schemas
Pydantic schemas for product-related API requests/responses
"""

from typing import Optional
from pydantic import Field
from app.schemas.base import BaseSchema, BaseResponse
from app.models.product import VATRate


# Product Category Schemas
class ProductCategoryBase(BaseSchema):
    """Base product category schema."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    parent_id: Optional[int] = None
    color: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    sort_order: int = 0


class ProductCategoryCreate(ProductCategoryBase):
    """Schema for creating a product category."""
    pass


class ProductCategoryUpdate(BaseSchema):
    """Schema for updating a product category."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    parent_id: Optional[int] = None
    color: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class ProductCategoryResponse(BaseResponse):
    """Schema for product category response."""
    name: str
    slug: str
    description: Optional[str]
    parent_id: Optional[int]
    color: Optional[str]
    sort_order: int
    is_active: bool
    tenant_id: str


# Product Schemas
class ProductBase(BaseSchema):
    """Base product schema."""
    name: str = Field(..., min_length=1, max_length=200)
    sku: Optional[str] = Field(None, max_length=100)
    barcode: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    category_id: Optional[int] = None
    price: float = Field(..., gt=0)
    cost: Optional[float] = Field(None, ge=0)
    vat_rate: VATRate = VATRate.STANDARD
    track_inventory: bool = True
    stock_quantity: int = Field(default=0, ge=0)
    min_stock_level: Optional[int] = Field(None, ge=0)
    is_available: bool = True
    image_url: Optional[str] = Field(None, max_length=500)


class ProductCreate(ProductBase):
    """Schema for creating a product."""
    pass


class ProductUpdate(BaseSchema):
    """Schema for updating a product."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    sku: Optional[str] = Field(None, max_length=100)
    barcode: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    category_id: Optional[int] = None
    price: Optional[float] = Field(None, gt=0)
    cost: Optional[float] = Field(None, ge=0)
    vat_rate: Optional[VATRate] = None
    track_inventory: Optional[bool] = None
    stock_quantity: Optional[int] = Field(None, ge=0)
    min_stock_level: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None
    is_available: Optional[bool] = None
    image_url: Optional[str] = Field(None, max_length=500)


class ProductResponse(BaseResponse):
    """Schema for product response."""
    name: str
    sku: Optional[str]
    barcode: Optional[str]
    description: Optional[str]
    category_id: Optional[int]
    price: float
    cost: Optional[float]
    vat_rate: str
    track_inventory: bool
    stock_quantity: int
    min_stock_level: Optional[int]
    is_active: bool
    is_available: bool
    image_url: Optional[str]
    tenant_id: str

    # Computed fields
    @property
    def net_price(self) -> float:
        """Calculate net price."""
        vat_rate = float(self.vat_rate)
        return round(self.price / (1 + vat_rate), 2)

    @property
    def vat_amount(self) -> float:
        """Calculate VAT amount."""
        return round(self.price - self.net_price, 2)

    @property
    def is_low_stock(self) -> bool:
        """Check if low stock."""
        if not self.track_inventory:
            return False
        return self.stock_quantity <= (self.min_stock_level or 0)


class ProductSearchParams(BaseSchema):
    """Schema for product search parameters."""
    q: Optional[str] = None  # Search query
    category_id: Optional[int] = None
    barcode: Optional[str] = None
    sku: Optional[str] = None
    is_available: Optional[bool] = None
    is_active: Optional[bool] = True
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=50, ge=1, le=100)


class StockAdjustment(BaseSchema):
    """Schema for stock adjustment."""
    quantity: int  # Positive to add, negative to remove
    reason: Optional[str] = None

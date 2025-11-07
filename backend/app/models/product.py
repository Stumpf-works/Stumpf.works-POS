"""
Product Models
Products, categories, and inventory management
"""

import enum

from sqlalchemy import Boolean, Column
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.models.base import BaseModel, TenantMixin


class ProductCategory(BaseModel, TenantMixin):
    """
    Product category for organizing products.
    """

    __tablename__ = "product_categories"

    name = Column(String(100), nullable=False)
    slug = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)

    # Parent category for nested categories
    parent_id = Column(Integer, ForeignKey("product_categories.id"), nullable=True)

    # Color for UI (hex code)
    color = Column(String(7), nullable=True)

    # Display order
    sort_order = Column(Integer, default=0, nullable=False)

    # Active status
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    parent = relationship(
        "ProductCategory", remote_side="ProductCategory.id", backref="subcategories"
    )
    # products = relationship("Product", back_populates="category")

    def __repr__(self) -> str:
        return f"<ProductCategory(id={self.id}, name={self.name})>"


class VATRate(str, enum.Enum):
    """German VAT rates."""

    STANDARD = "0.19"  # 19% - Standard rate
    REDUCED = "0.07"  # 7% - Reduced rate (food, books, etc.)
    ZERO = "0.00"  # 0% - Exempt


class Product(BaseModel, TenantMixin):
    """
    Product model for items sold through POS.
    """

    __tablename__ = "products"

    # Basic Information
    name = Column(String(200), nullable=False)
    sku = Column(String(100), nullable=True, index=True)  # Stock Keeping Unit
    barcode = Column(String(100), nullable=True, index=True)
    description = Column(Text, nullable=True)

    # Category
    category_id = Column(Integer, ForeignKey("product_categories.id"), nullable=True)

    # Pricing (in cents to avoid floating point issues, or use Decimal)
    price = Column(Float, nullable=False)  # Gross price (including VAT)
    cost = Column(Float, nullable=True)  # Cost price (for margin calculation)

    # VAT
    vat_rate = Column(SQLEnum(VATRate), default=VATRate.STANDARD, nullable=False)

    # Inventory
    track_inventory = Column(Boolean, default=True, nullable=False)
    stock_quantity = Column(Integer, default=0, nullable=False)
    min_stock_level = Column(Integer, default=0, nullable=True)

    # Attributes
    is_active = Column(Boolean, default=True, nullable=False)
    is_available = Column(Boolean, default=True, nullable=False)

    # Image
    image_url = Column(String(500), nullable=True)

    # Relationships
    category = relationship("ProductCategory", backref="products")
    # transaction_items = relationship("TransactionItem", back_populates="product")

    def __repr__(self) -> str:
        return f"<Product(id={self.id}, name={self.name}, price={self.price})>"

    @property
    def net_price(self) -> float:
        """Calculate net price (without VAT)."""
        vat_rate = float(self.vat_rate.value)
        return round(self.price / (1 + vat_rate), 2)

    @property
    def vat_amount(self) -> float:
        """Calculate VAT amount."""
        return round(self.price - self.net_price, 2)

    @property
    def is_low_stock(self) -> bool:
        """Check if product is low on stock."""
        if not self.track_inventory:
            return False
        return self.stock_quantity <= (self.min_stock_level or 0)

    @property
    def is_out_of_stock(self) -> bool:
        """Check if product is out of stock."""
        if not self.track_inventory:
            return False
        return self.stock_quantity <= 0


# Alias for backward compatibility with tests
Category = ProductCategory

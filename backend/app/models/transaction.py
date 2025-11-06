"""
Transaction Models
Sales transactions and receipts
"""

from sqlalchemy import Column, String, Float, Integer, ForeignKey, Enum as SQLEnum, Text, Boolean, DateTime
from sqlalchemy.orm import relationship
import enum
from datetime import datetime

from app.models.base import BaseModel, TenantMixin


class PaymentMethod(str, enum.Enum):
    """Payment method enumeration."""

    CASH = "cash"
    CARD = "card"
    SUMUP = "sumup"
    BANK_TRANSFER = "bank_transfer"
    OTHER = "other"


class TransactionStatus(str, enum.Enum):
    """Transaction status enumeration."""

    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class Transaction(BaseModel, TenantMixin):
    """
    Transaction (Receipt) model.

    Represents a completed or pending sale transaction.
    Must be signed by TSE for German compliance.
    """

    __tablename__ = "transactions"

    # Receipt Information
    receipt_number = Column(String(50), unique=True, nullable=False, index=True)

    # User & Location
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    # location_id = Column(Integer, ForeignKey("locations.id"), nullable=True)

    # Status
    status = Column(SQLEnum(TransactionStatus), default=TransactionStatus.PENDING, nullable=False)

    # Amounts (in EUR)
    subtotal = Column(Float, nullable=False)  # Sum of items before tax
    tax_amount = Column(Float, nullable=False)  # Total VAT amount
    total = Column(Float, nullable=False)  # Final amount to pay
    discount_amount = Column(Float, default=0.0, nullable=False)

    # Payment
    payment_method = Column(SQLEnum(PaymentMethod), nullable=False)
    payment_reference = Column(String(255), nullable=True)  # External payment ID (SumUp, etc.)
    cash_given = Column(Float, nullable=True)  # Amount given by customer (for cash)
    cash_change = Column(Float, nullable=True)  # Change returned

    # TSE Signature (Cloud-TSE / Fiskaly)
    tse_transaction_id = Column(String(255), nullable=True, index=True)
    tse_signature = Column(Text, nullable=True)
    tse_time_start = Column(DateTime, nullable=True)
    tse_time_end = Column(DateTime, nullable=True)
    tse_serial_number = Column(String(255), nullable=True)
    is_tse_signed = Column(Boolean, default=False, nullable=False)

    # Additional Info
    notes = Column(Text, nullable=True)
    customer_name = Column(String(255), nullable=True)
    customer_email = Column(String(255), nullable=True)

    # Timestamps
    completed_at = Column(DateTime, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", backref="transactions")
    items = relationship("TransactionItem", back_populates="transaction", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Transaction(id={self.id}, receipt_number={self.receipt_number}, total={self.total})>"

    @property
    def is_completed(self) -> bool:
        """Check if transaction is completed."""
        return self.status == TransactionStatus.COMPLETED

    @property
    def requires_tse_signature(self) -> bool:
        """Check if transaction requires TSE signature."""
        # All completed transactions in Germany require TSE signature
        return self.is_completed and not self.is_tse_signed


class TransactionItem(BaseModel):
    """
    Individual item in a transaction.
    """

    __tablename__ = "transaction_items"

    # Transaction reference
    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=False)

    # Product reference
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    # Product details (snapshot at time of sale)
    product_name = Column(String(200), nullable=False)
    product_sku = Column(String(100), nullable=True)

    # Quantity & Pricing
    quantity = Column(Integer, default=1, nullable=False)
    unit_price = Column(Float, nullable=False)  # Price per unit (gross)
    vat_rate = Column(Float, nullable=False)  # VAT rate as decimal (0.19 = 19%)

    # Calculated amounts
    subtotal = Column(Float, nullable=False)  # quantity * unit_price
    tax_amount = Column(Float, nullable=False)  # VAT amount
    total = Column(Float, nullable=False)  # Subtotal (including VAT)

    # Discount
    discount_amount = Column(Float, default=0.0, nullable=False)

    # Relationships
    transaction = relationship("Transaction", back_populates="items")
    product = relationship("Product", backref="transaction_items")

    def __repr__(self) -> str:
        return f"<TransactionItem(id={self.id}, product={self.product_name}, quantity={self.quantity})>"

    @property
    def net_price(self) -> float:
        """Calculate net price per unit."""
        return round(self.unit_price / (1 + self.vat_rate), 2)

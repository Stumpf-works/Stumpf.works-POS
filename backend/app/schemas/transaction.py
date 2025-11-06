"""
Transaction Schemas
Pydantic schemas for transaction-related API requests/responses
"""

from typing import List, Optional
from datetime import datetime
from pydantic import Field
from app.schemas.base import BaseSchema, BaseResponse
from app.models.transaction import PaymentMethod, TransactionStatus


# Transaction Item Schemas
class TransactionItemCreate(BaseSchema):
    """Schema for creating a transaction item."""
    product_id: int
    quantity: int = Field(..., gt=0)
    discount_amount: float = Field(default=0.0, ge=0)


class TransactionItemResponse(BaseSchema):
    """Schema for transaction item response."""
    id: int
    product_id: int
    product_name: str
    product_sku: Optional[str]
    quantity: int
    unit_price: float
    vat_rate: float
    subtotal: float
    tax_amount: float
    total: float
    discount_amount: float


# Transaction Schemas
class TransactionCreate(BaseSchema):
    """Schema for creating a transaction."""
    items: List[TransactionItemCreate] = Field(..., min_length=1)
    payment_method: PaymentMethod
    cash_given: Optional[float] = Field(None, ge=0)
    discount_amount: float = Field(default=0.0, ge=0)
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    notes: Optional[str] = None


class TransactionResponse(BaseResponse):
    """Schema for transaction response."""
    receipt_number: str
    user_id: int
    status: TransactionStatus
    subtotal: float
    tax_amount: float
    total: float
    discount_amount: float
    payment_method: PaymentMethod
    payment_reference: Optional[str]
    cash_given: Optional[float]
    cash_change: Optional[float]
    tse_transaction_id: Optional[str]
    tse_signature: Optional[str]
    is_tse_signed: bool
    notes: Optional[str]
    customer_name: Optional[str]
    customer_email: Optional[str]
    completed_at: Optional[datetime]
    cancelled_at: Optional[datetime]
    items: List[TransactionItemResponse]
    tenant_id: str


class TransactionListResponse(BaseResponse):
    """Schema for transaction list (without items for performance)."""
    receipt_number: str
    user_id: int
    status: TransactionStatus
    total: float
    payment_method: PaymentMethod
    is_tse_signed: bool
    completed_at: Optional[datetime]
    tenant_id: str


class TransactionSearchParams(BaseSchema):
    """Schema for transaction search parameters."""
    receipt_number: Optional[str] = None
    user_id: Optional[int] = None
    status: Optional[TransactionStatus] = None
    payment_method: Optional[PaymentMethod] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=50, ge=1, le=100)


class TransactionStats(BaseSchema):
    """Schema for transaction statistics."""
    total_transactions: int
    total_revenue: float
    total_tax: float
    avg_transaction_value: float
    payment_methods: dict
    status_breakdown: dict

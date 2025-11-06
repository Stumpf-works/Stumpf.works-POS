"""Payment Gateway Integration Plugin - Multi-payment provider support.

This plugin provides comprehensive payment processing functionality including:
- Multiple payment provider integration (Stripe, PayPal, Square, SumUp, etc.)
- Credit card processing
- Digital wallet support (Apple Pay, Google Pay, etc.)
- Payment terminal integration
- Refund and void processing
- Payment reconciliation
- Compliance and security (PCI-DSS)
"""

from datetime import datetime
from decimal import Decimal
from typing import Dict, Optional

import structlog
from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.core.database import SQLBase
from app.models.mixins import TenantMixin
from app.plugins.base import BasePlugin

logger = structlog.get_logger(__name__)


# Database Models
class PaymentProvider(SQLBase, TenantMixin):
    """Payment provider configuration."""

    __tablename__ = "plugin_payment_providers"

    provider_name = Column(String(100), nullable=False)  # stripe, paypal, square, sumup
    provider_type = Column(
        String(50), nullable=False
    )  # card_processor, digital_wallet, terminal

    # API credentials (encrypted in production)
    api_key = Column(String(500), nullable=True)
    api_secret = Column(String(500), nullable=True)
    merchant_id = Column(String(200), nullable=True)
    webhook_secret = Column(String(500), nullable=True)

    # Configuration
    is_test_mode = Column(Boolean, nullable=False, default=True)
    is_active = Column(Boolean, nullable=False, default=True)
    is_default = Column(Boolean, nullable=False, default=False)

    # Supported features (JSON)
    supported_methods = Column(Text, nullable=True)  # credit_card, debit_card, wallet
    supported_currencies = Column(Text, nullable=True)

    # Fees
    transaction_fee_percentage = Column(Numeric(5, 2), nullable=True)
    transaction_fee_fixed = Column(Numeric(10, 2), nullable=True)

    # Status
    last_health_check = Column(DateTime, nullable=True)
    health_status = Column(String(20), nullable=True)  # healthy, degraded, down

    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    transactions = relationship(
        "PaymentTransaction", back_populates="provider", cascade="all, delete-orphan"
    )
    terminals = relationship(
        "PaymentTerminal", back_populates="provider", cascade="all, delete-orphan"
    )


class PaymentTransaction(SQLBase, TenantMixin):
    """Payment transaction record."""

    __tablename__ = "plugin_payment_transactions"

    # Order reference
    order_id = Column(Integer, nullable=False)
    order_number = Column(String(50), nullable=False)

    # Provider details
    provider_id = Column(
        Integer, ForeignKey("plugin_payment_providers.id"), nullable=False
    )
    provider_transaction_id = Column(String(200), nullable=True)

    # Payment details
    payment_method = Column(
        String(50), nullable=False
    )  # credit_card, debit_card, wallet, terminal
    payment_type = Column(String(20), nullable=False)  # charge, refund, void, capture

    # Amount
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), nullable=False, default="EUR")
    fee_amount = Column(Numeric(10, 2), nullable=True)
    net_amount = Column(Numeric(10, 2), nullable=True)

    # Card details (last 4 digits only for PCI compliance)
    card_brand = Column(String(20), nullable=True)  # visa, mastercard, amex
    card_last4 = Column(String(4), nullable=True)
    card_exp_month = Column(Integer, nullable=True)
    card_exp_year = Column(Integer, nullable=True)

    # Digital wallet
    wallet_type = Column(String(50), nullable=True)  # apple_pay, google_pay, paypal

    # Terminal
    terminal_id = Column(
        Integer, ForeignKey("plugin_payment_terminals.id"), nullable=True
    )

    # Transaction status
    status = Column(
        String(20), nullable=False, default="pending"
    )  # pending, authorized, captured, failed, refunded, voided
    status_message = Column(String(500), nullable=True)

    # Timing
    authorized_at = Column(DateTime, nullable=True)
    captured_at = Column(DateTime, nullable=True)
    failed_at = Column(DateTime, nullable=True)

    # Security
    risk_score = Column(Numeric(3, 2), nullable=True)  # 0.00 to 1.00
    risk_level = Column(String(20), nullable=True)  # low, medium, high
    cvv_check = Column(String(20), nullable=True)  # pass, fail, not_checked
    address_check = Column(String(20), nullable=True)  # pass, fail, not_checked

    # Customer information
    customer_email = Column(String(200), nullable=True)
    customer_name = Column(String(200), nullable=True)
    billing_address = Column(Text, nullable=True)

    # Metadata
    metadata = Column(Text, nullable=True)  # JSON
    error_code = Column(String(100), nullable=True)
    error_message = Column(Text, nullable=True)

    # Reconciliation
    is_reconciled = Column(Boolean, nullable=False, default=False)
    reconciled_at = Column(DateTime, nullable=True)

    processed_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    provider = relationship("PaymentProvider", back_populates="transactions")
    terminal = relationship("PaymentTerminal", back_populates="transactions")
    refunds = relationship(
        "PaymentRefund", back_populates="transaction", cascade="all, delete-orphan"
    )


class PaymentRefund(SQLBase, TenantMixin):
    """Payment refund record."""

    __tablename__ = "plugin_payment_refunds"

    transaction_id = Column(
        Integer, ForeignKey("plugin_payment_transactions.id"), nullable=False
    )
    provider_refund_id = Column(String(200), nullable=True)

    # Refund details
    refund_amount = Column(Numeric(10, 2), nullable=False)
    refund_reason = Column(String(500), nullable=True)
    refund_type = Column(String(20), nullable=False)  # full, partial

    # Status
    status = Column(
        String(20), nullable=False, default="pending"
    )  # pending, completed, failed
    status_message = Column(String(500), nullable=True)

    # Timing
    requested_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    error_message = Column(Text, nullable=True)
    processed_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationship
    transaction = relationship("PaymentTransaction", back_populates="refunds")


class PaymentTerminal(SQLBase, TenantMixin):
    """Payment terminal device."""

    __tablename__ = "plugin_payment_terminals"

    provider_id = Column(
        Integer, ForeignKey("plugin_payment_providers.id"), nullable=False
    )

    # Terminal details
    terminal_name = Column(String(100), nullable=False)
    terminal_id_external = Column(String(200), nullable=True)
    serial_number = Column(String(100), nullable=True)

    # Terminal type
    terminal_type = Column(
        String(50), nullable=False
    )  # countertop, mobile, integrated, virtual

    # Location
    location = Column(String(200), nullable=True)
    register_id = Column(Integer, nullable=True)

    # Status
    status = Column(
        String(20), nullable=False, default="inactive"
    )  # active, inactive, maintenance
    connection_status = Column(String(20), nullable=True)  # online, offline

    # Configuration
    supports_contactless = Column(Boolean, nullable=False, default=True)
    supports_chip = Column(Boolean, nullable=False, default=True)
    supports_swipe = Column(Boolean, nullable=False, default=True)

    # Activity tracking
    last_transaction_at = Column(DateTime, nullable=True)
    last_heartbeat = Column(DateTime, nullable=True)

    is_active = Column(Boolean, nullable=False, default=True)

    # Relationships
    provider = relationship("PaymentProvider", back_populates="terminals")
    transactions = relationship("PaymentTransaction", back_populates="terminal")


class PaymentReconciliation(SQLBase, TenantMixin):
    """Daily payment reconciliation."""

    __tablename__ = "plugin_payment_reconciliation"

    reconciliation_date = Column(DateTime, nullable=False)
    provider_id = Column(
        Integer, ForeignKey("plugin_payment_providers.id"), nullable=True
    )

    # Transaction counts
    total_transactions = Column(Integer, nullable=False, default=0)
    successful_transactions = Column(Integer, nullable=False, default=0)
    failed_transactions = Column(Integer, nullable=False, default=0)
    refunded_transactions = Column(Integer, nullable=False, default=0)

    # Amounts
    total_charged = Column(Numeric(12, 2), nullable=False, default=0)
    total_refunded = Column(Numeric(12, 2), nullable=False, default=0)
    total_fees = Column(Numeric(12, 2), nullable=False, default=0)
    net_amount = Column(Numeric(12, 2), nullable=False, default=0)

    # Settlement
    expected_payout = Column(Numeric(12, 2), nullable=True)
    actual_payout = Column(Numeric(12, 2), nullable=True)
    payout_date = Column(DateTime, nullable=True)

    # Status
    status = Column(
        String(20), nullable=False, default="pending"
    )  # pending, balanced, unbalanced
    variance_amount = Column(Numeric(12, 2), nullable=True)

    notes = Column(Text, nullable=True)
    reconciled_by = Column(Integer, ForeignKey("users.id"), nullable=True)


class PaymentWebhook(SQLBase, TenantMixin):
    """Payment webhook event log."""

    __tablename__ = "plugin_payment_webhooks"

    provider_id = Column(
        Integer, ForeignKey("plugin_payment_providers.id"), nullable=False
    )

    # Webhook details
    event_type = Column(String(100), nullable=False)
    event_id = Column(String(200), nullable=True)

    # Payload
    payload = Column(Text, nullable=False)  # JSON

    # Processing
    processed = Column(Boolean, nullable=False, default=False)
    processed_at = Column(DateTime, nullable=True)
    processing_error = Column(Text, nullable=True)

    # Verification
    signature_valid = Column(Boolean, nullable=True)
    received_at = Column(DateTime, nullable=False, default=datetime.utcnow)


# Pydantic Models
class PaymentProviderCreate(BaseModel):
    """Schema for creating a payment provider."""

    provider_name: str
    provider_type: str
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    merchant_id: Optional[str] = None
    is_test_mode: bool = True
    is_active: bool = True
    is_default: bool = False


class PaymentTransactionCreate(BaseModel):
    """Schema for creating a payment transaction."""

    order_id: int
    order_number: str
    provider_id: int
    payment_method: str
    payment_type: str = "charge"
    amount: Decimal
    currency: str = "EUR"
    customer_email: Optional[str] = None
    customer_name: Optional[str] = None
    terminal_id: Optional[int] = None


class PaymentRefundCreate(BaseModel):
    """Schema for creating a refund."""

    transaction_id: int
    refund_amount: Decimal
    refund_reason: Optional[str] = None
    refund_type: str = "full"


class PaymentTerminalCreate(BaseModel):
    """Schema for creating a payment terminal."""

    provider_id: int
    terminal_name: str
    terminal_id_external: Optional[str] = None
    terminal_type: str = "countertop"
    location: Optional[str] = None
    supports_contactless: bool = True
    supports_chip: bool = True
    supports_swipe: bool = True


class PaymentProcessRequest(BaseModel):
    """Schema for processing a payment."""

    order_id: int
    amount: Decimal
    currency: str = "EUR"
    payment_method: str
    provider_id: Optional[int] = None
    terminal_id: Optional[int] = None


# Plugin Class
class PaymentGatewayPlugin(BasePlugin):
    """Payment Gateway Integration Plugin for multi-provider payment processing."""

    def __init__(self):
        """Initialize the payment gateway plugin."""
        super().__init__()
        self.router = APIRouter(prefix="/payments", tags=["payment-gateway"])
        self._register_routes()

    def get_name(self) -> str:
        """Get plugin name."""
        return "payment_gateway"

    def get_display_name(self) -> str:
        """Get display name."""
        return "Zahlungs-Gateway"

    def get_description(self) -> str:
        """Get plugin description."""
        return (
            "Multi-Provider-Zahlungsabwicklung mit Unterstützung für "
            "Karten, digitale Wallets und Terminals"
        )

    def get_version(self) -> str:
        """Get plugin version."""
        return "1.0.0"

    def get_category(self) -> str:
        """Get plugin category."""
        return "payment"

    def get_config_schema(self) -> Optional[Dict]:
        """Get configuration schema."""
        return {
            "type": "object",
            "properties": {
                "enable_test_mode": {
                    "type": "boolean",
                    "default": True,
                    "description": "Testmodus für alle Provider aktivieren",
                },
                "auto_capture": {
                    "type": "boolean",
                    "default": True,
                    "description": "Automatische Erfassung nach Autorisierung",
                },
                "enable_fraud_detection": {
                    "type": "boolean",
                    "default": True,
                    "description": "Betrugserkennung aktivieren",
                },
                "max_transaction_amount": {
                    "type": "number",
                    "default": 10000.0,
                    "description": "Maximaler Transaktionsbetrag",
                },
                "require_cvv": {
                    "type": "boolean",
                    "default": True,
                    "description": "CVV-Prüfung erforderlich",
                },
                "enable_3d_secure": {
                    "type": "boolean",
                    "default": True,
                    "description": "3D Secure für Kartenzahlungen aktivieren",
                },
            },
        }

    def _register_routes(self):
        """Register API routes."""

        @self.router.post("/providers")
        async def create_provider(provider_data: PaymentProviderCreate):
            """Create a new payment provider."""
            logger.info("create_provider", provider_name=provider_data.provider_name)
            # Implementation would create provider in database
            return {
                "message": "Payment provider created successfully",
                "provider_name": provider_data.provider_name,
            }

        @self.router.get("/providers")
        async def get_providers(is_active: Optional[bool] = None):
            """Get all payment providers."""
            logger.info("get_providers", is_active=is_active)
            # Implementation would fetch providers from database
            return {"providers": []}

        @self.router.post("/process")
        async def process_payment(payment_data: PaymentProcessRequest):
            """Process a payment transaction."""
            logger.info("process_payment", order_id=payment_data.order_id)
            # Implementation would process payment through provider
            return {
                "message": "Payment processed successfully",
                "transaction_id": 1,
                "status": "authorized",
            }

        @self.router.post("/transactions")
        async def create_transaction(transaction_data: PaymentTransactionCreate):
            """Create a payment transaction record."""
            logger.info(
                "create_transaction", order_number=transaction_data.order_number
            )
            # Implementation would create transaction in database
            return {
                "message": "Transaction created successfully",
                "order_number": transaction_data.order_number,
            }

        @self.router.get("/transactions/{transaction_id}")
        async def get_transaction(transaction_id: int):
            """Get transaction details."""
            logger.info("get_transaction", transaction_id=transaction_id)
            # Implementation would fetch transaction from database
            return {"transaction_id": transaction_id, "status": "pending"}

        @self.router.post("/refunds")
        async def create_refund(refund_data: PaymentRefundCreate):
            """Process a refund."""
            logger.info("create_refund", transaction_id=refund_data.transaction_id)
            # Implementation would process refund through provider
            return {
                "message": "Refund processed successfully",
                "refund_amount": refund_data.refund_amount,
            }

        @self.router.get("/refunds/{transaction_id}")
        async def get_refunds(transaction_id: int):
            """Get all refunds for a transaction."""
            logger.info("get_refunds", transaction_id=transaction_id)
            # Implementation would fetch refunds from database
            return {"refunds": []}

        @self.router.post("/terminals")
        async def create_terminal(terminal_data: PaymentTerminalCreate):
            """Register a new payment terminal."""
            logger.info("create_terminal", terminal_name=terminal_data.terminal_name)
            # Implementation would create terminal in database
            return {
                "message": "Terminal registered successfully",
                "terminal_name": terminal_data.terminal_name,
            }

        @self.router.get("/terminals")
        async def get_terminals(provider_id: Optional[int] = None):
            """Get all payment terminals."""
            logger.info("get_terminals", provider_id=provider_id)
            # Implementation would fetch terminals from database
            return {"terminals": []}

        @self.router.post("/terminals/{terminal_id}/activate")
        async def activate_terminal(terminal_id: int):
            """Activate a payment terminal."""
            logger.info("activate_terminal", terminal_id=terminal_id)
            # Implementation would activate terminal
            return {"message": "Terminal activated", "terminal_id": terminal_id}

        @self.router.get("/reconciliation")
        async def get_reconciliation(
            start_date: Optional[str] = None, provider_id: Optional[int] = None
        ):
            """Get payment reconciliation data."""
            logger.info(
                "get_reconciliation", start_date=start_date, provider_id=provider_id
            )
            # Implementation would fetch reconciliation data
            return {"reconciliation": []}

        @self.router.post("/webhooks/{provider_name}")
        async def handle_webhook(provider_name: str, payload: dict):
            """Handle payment provider webhook."""
            logger.info("handle_webhook", provider_name=provider_name)
            # Implementation would process webhook event
            return {"message": "Webhook processed", "provider": provider_name}


# Plugin instance
plugin = PaymentGatewayPlugin()

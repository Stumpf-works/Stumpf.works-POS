"""Add payment gateway plugin tables

Revision ID: 011_payment_gateway
Revises: 010_advanced_analytics
Create Date: 2025-11-06

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "011_payment_gateway"
down_revision: Union[str, None] = "010_advanced_analytics"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create payment gateway tables."""
    # Create payment_providers table
    op.create_table(
        "plugin_payment_providers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("tenant_id", sa.String(length=100), nullable=False),
        sa.Column("provider_name", sa.String(length=100), nullable=False),
        sa.Column("provider_type", sa.String(length=50), nullable=False),
        sa.Column("api_key", sa.String(length=500), nullable=True),
        sa.Column("api_secret", sa.String(length=500), nullable=True),
        sa.Column("merchant_id", sa.String(length=200), nullable=True),
        sa.Column("webhook_secret", sa.String(length=500), nullable=True),
        sa.Column("is_test_mode", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("is_default", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("supported_methods", sa.Text(), nullable=True),
        sa.Column("supported_currencies", sa.Text(), nullable=True),
        sa.Column("transaction_fee_percentage", sa.Numeric(5, 2), nullable=True),
        sa.Column("transaction_fee_fixed", sa.Numeric(10, 2), nullable=True),
        sa.Column("last_health_check", sa.DateTime(), nullable=True),
        sa.Column("health_status", sa.String(length=20), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["created_by"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_plugin_payment_providers_tenant_id",
        "plugin_payment_providers",
        ["tenant_id"],
    )
    op.create_index(
        "ix_plugin_payment_providers_provider_name",
        "plugin_payment_providers",
        ["provider_name"],
    )

    # Create payment_terminals table
    op.create_table(
        "plugin_payment_terminals",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("tenant_id", sa.String(length=100), nullable=False),
        sa.Column("provider_id", sa.Integer(), nullable=False),
        sa.Column("terminal_name", sa.String(length=100), nullable=False),
        sa.Column("terminal_id_external", sa.String(length=200), nullable=True),
        sa.Column("serial_number", sa.String(length=100), nullable=True),
        sa.Column("terminal_type", sa.String(length=50), nullable=False),
        sa.Column("location", sa.String(length=200), nullable=True),
        sa.Column("register_id", sa.Integer(), nullable=True),
        sa.Column(
            "status", sa.String(length=20), nullable=False, server_default="inactive"
        ),
        sa.Column("connection_status", sa.String(length=20), nullable=True),
        sa.Column(
            "supports_contactless", sa.Boolean(), nullable=False, server_default="true"
        ),
        sa.Column("supports_chip", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column(
            "supports_swipe", sa.Boolean(), nullable=False, server_default="true"
        ),
        sa.Column("last_transaction_at", sa.DateTime(), nullable=True),
        sa.Column("last_heartbeat", sa.DateTime(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.ForeignKeyConstraint(
            ["provider_id"],
            ["plugin_payment_providers.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_plugin_payment_terminals_tenant_id",
        "plugin_payment_terminals",
        ["tenant_id"],
    )
    op.create_index(
        "ix_plugin_payment_terminals_provider_id",
        "plugin_payment_terminals",
        ["provider_id"],
    )

    # Create payment_transactions table
    op.create_table(
        "plugin_payment_transactions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("tenant_id", sa.String(length=100), nullable=False),
        sa.Column("order_id", sa.Integer(), nullable=False),
        sa.Column("order_number", sa.String(length=50), nullable=False),
        sa.Column("provider_id", sa.Integer(), nullable=False),
        sa.Column("provider_transaction_id", sa.String(length=200), nullable=True),
        sa.Column("payment_method", sa.String(length=50), nullable=False),
        sa.Column("payment_type", sa.String(length=20), nullable=False),
        sa.Column("amount", sa.Numeric(10, 2), nullable=False),
        sa.Column(
            "currency", sa.String(length=3), nullable=False, server_default="EUR"
        ),
        sa.Column("fee_amount", sa.Numeric(10, 2), nullable=True),
        sa.Column("net_amount", sa.Numeric(10, 2), nullable=True),
        sa.Column("card_brand", sa.String(length=20), nullable=True),
        sa.Column("card_last4", sa.String(length=4), nullable=True),
        sa.Column("card_exp_month", sa.Integer(), nullable=True),
        sa.Column("card_exp_year", sa.Integer(), nullable=True),
        sa.Column("wallet_type", sa.String(length=50), nullable=True),
        sa.Column("terminal_id", sa.Integer(), nullable=True),
        sa.Column(
            "status", sa.String(length=20), nullable=False, server_default="pending"
        ),
        sa.Column("status_message", sa.String(length=500), nullable=True),
        sa.Column("authorized_at", sa.DateTime(), nullable=True),
        sa.Column("captured_at", sa.DateTime(), nullable=True),
        sa.Column("failed_at", sa.DateTime(), nullable=True),
        sa.Column("risk_score", sa.Numeric(3, 2), nullable=True),
        sa.Column("risk_level", sa.String(length=20), nullable=True),
        sa.Column("cvv_check", sa.String(length=20), nullable=True),
        sa.Column("address_check", sa.String(length=20), nullable=True),
        sa.Column("customer_email", sa.String(length=200), nullable=True),
        sa.Column("customer_name", sa.String(length=200), nullable=True),
        sa.Column("billing_address", sa.Text(), nullable=True),
        sa.Column("metadata", sa.Text(), nullable=True),
        sa.Column("error_code", sa.String(length=100), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column(
            "is_reconciled", sa.Boolean(), nullable=False, server_default="false"
        ),
        sa.Column("reconciled_at", sa.DateTime(), nullable=True),
        sa.Column("processed_by", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["provider_id"],
            ["plugin_payment_providers.id"],
        ),
        sa.ForeignKeyConstraint(
            ["terminal_id"],
            ["plugin_payment_terminals.id"],
        ),
        sa.ForeignKeyConstraint(
            ["processed_by"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_plugin_payment_transactions_tenant_id",
        "plugin_payment_transactions",
        ["tenant_id"],
    )
    op.create_index(
        "ix_plugin_payment_transactions_order_number",
        "plugin_payment_transactions",
        ["order_number"],
    )
    op.create_index(
        "ix_plugin_payment_transactions_provider_id",
        "plugin_payment_transactions",
        ["provider_id"],
    )
    op.create_index(
        "ix_plugin_payment_transactions_status",
        "plugin_payment_transactions",
        ["status"],
    )

    # Create payment_refunds table
    op.create_table(
        "plugin_payment_refunds",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("tenant_id", sa.String(length=100), nullable=False),
        sa.Column("transaction_id", sa.Integer(), nullable=False),
        sa.Column("provider_refund_id", sa.String(length=200), nullable=True),
        sa.Column("refund_amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("refund_reason", sa.String(length=500), nullable=True),
        sa.Column("refund_type", sa.String(length=20), nullable=False),
        sa.Column(
            "status", sa.String(length=20), nullable=False, server_default="pending"
        ),
        sa.Column("status_message", sa.String(length=500), nullable=True),
        sa.Column("requested_at", sa.DateTime(), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("processed_by", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["transaction_id"],
            ["plugin_payment_transactions.id"],
        ),
        sa.ForeignKeyConstraint(
            ["processed_by"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_plugin_payment_refunds_tenant_id",
        "plugin_payment_refunds",
        ["tenant_id"],
    )
    op.create_index(
        "ix_plugin_payment_refunds_transaction_id",
        "plugin_payment_refunds",
        ["transaction_id"],
    )

    # Create payment_reconciliation table
    op.create_table(
        "plugin_payment_reconciliation",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("tenant_id", sa.String(length=100), nullable=False),
        sa.Column("reconciliation_date", sa.DateTime(), nullable=False),
        sa.Column("provider_id", sa.Integer(), nullable=True),
        sa.Column(
            "total_transactions", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column(
            "successful_transactions", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column(
            "failed_transactions", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column(
            "refunded_transactions", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column(
            "total_charged", sa.Numeric(12, 2), nullable=False, server_default="0"
        ),
        sa.Column(
            "total_refunded", sa.Numeric(12, 2), nullable=False, server_default="0"
        ),
        sa.Column("total_fees", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("net_amount", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("expected_payout", sa.Numeric(12, 2), nullable=True),
        sa.Column("actual_payout", sa.Numeric(12, 2), nullable=True),
        sa.Column("payout_date", sa.DateTime(), nullable=True),
        sa.Column(
            "status", sa.String(length=20), nullable=False, server_default="pending"
        ),
        sa.Column("variance_amount", sa.Numeric(12, 2), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("reconciled_by", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["provider_id"],
            ["plugin_payment_providers.id"],
        ),
        sa.ForeignKeyConstraint(
            ["reconciled_by"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_plugin_payment_reconciliation_tenant_id",
        "plugin_payment_reconciliation",
        ["tenant_id"],
    )
    op.create_index(
        "ix_plugin_payment_reconciliation_reconciliation_date",
        "plugin_payment_reconciliation",
        ["reconciliation_date"],
    )

    # Create payment_webhooks table
    op.create_table(
        "plugin_payment_webhooks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("tenant_id", sa.String(length=100), nullable=False),
        sa.Column("provider_id", sa.Integer(), nullable=False),
        sa.Column("event_type", sa.String(length=100), nullable=False),
        sa.Column("event_id", sa.String(length=200), nullable=True),
        sa.Column("payload", sa.Text(), nullable=False),
        sa.Column("processed", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("processed_at", sa.DateTime(), nullable=True),
        sa.Column("processing_error", sa.Text(), nullable=True),
        sa.Column("signature_valid", sa.Boolean(), nullable=True),
        sa.Column("received_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["provider_id"],
            ["plugin_payment_providers.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_plugin_payment_webhooks_tenant_id",
        "plugin_payment_webhooks",
        ["tenant_id"],
    )
    op.create_index(
        "ix_plugin_payment_webhooks_provider_id",
        "plugin_payment_webhooks",
        ["provider_id"],
    )
    op.create_index(
        "ix_plugin_payment_webhooks_received_at",
        "plugin_payment_webhooks",
        ["received_at"],
    )


def downgrade() -> None:
    """Drop payment gateway tables."""
    op.drop_index(
        "ix_plugin_payment_webhooks_received_at",
        table_name="plugin_payment_webhooks",
    )
    op.drop_index(
        "ix_plugin_payment_webhooks_provider_id",
        table_name="plugin_payment_webhooks",
    )
    op.drop_index(
        "ix_plugin_payment_webhooks_tenant_id",
        table_name="plugin_payment_webhooks",
    )
    op.drop_table("plugin_payment_webhooks")

    op.drop_index(
        "ix_plugin_payment_reconciliation_reconciliation_date",
        table_name="plugin_payment_reconciliation",
    )
    op.drop_index(
        "ix_plugin_payment_reconciliation_tenant_id",
        table_name="plugin_payment_reconciliation",
    )
    op.drop_table("plugin_payment_reconciliation")

    op.drop_index(
        "ix_plugin_payment_refunds_transaction_id",
        table_name="plugin_payment_refunds",
    )
    op.drop_index(
        "ix_plugin_payment_refunds_tenant_id",
        table_name="plugin_payment_refunds",
    )
    op.drop_table("plugin_payment_refunds")

    op.drop_index(
        "ix_plugin_payment_transactions_status",
        table_name="plugin_payment_transactions",
    )
    op.drop_index(
        "ix_plugin_payment_transactions_provider_id",
        table_name="plugin_payment_transactions",
    )
    op.drop_index(
        "ix_plugin_payment_transactions_order_number",
        table_name="plugin_payment_transactions",
    )
    op.drop_index(
        "ix_plugin_payment_transactions_tenant_id",
        table_name="plugin_payment_transactions",
    )
    op.drop_table("plugin_payment_transactions")

    op.drop_index(
        "ix_plugin_payment_terminals_provider_id",
        table_name="plugin_payment_terminals",
    )
    op.drop_index(
        "ix_plugin_payment_terminals_tenant_id",
        table_name="plugin_payment_terminals",
    )
    op.drop_table("plugin_payment_terminals")

    op.drop_index(
        "ix_plugin_payment_providers_provider_name",
        table_name="plugin_payment_providers",
    )
    op.drop_index(
        "ix_plugin_payment_providers_tenant_id",
        table_name="plugin_payment_providers",
    )
    op.drop_table("plugin_payment_providers")

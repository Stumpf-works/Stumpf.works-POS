"""Add loyalty program plugin tables

Revision ID: 005_loyalty_program
Revises: 004_employee_time_tracking
Create Date: 2025-11-06

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "005_loyalty_program"
down_revision: Union[str, None] = "004_employee_time_tracking"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create loyalty program tables."""
    # Create loyalty_customers table
    op.create_table(
        "plugin_loyalty_customers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("tenant_id", sa.String(length=100), nullable=False),
        sa.Column("customer_name", sa.String(length=200), nullable=False),
        sa.Column("email", sa.String(length=200), nullable=True),
        sa.Column("phone", sa.String(length=50), nullable=True),
        sa.Column("card_number", sa.String(length=50), nullable=False, unique=True),
        sa.Column("qr_code", sa.String(length=200), nullable=True),
        sa.Column("points_balance", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("lifetime_points", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "tier", sa.String(length=20), nullable=False, server_default="bronze"
        ),
        sa.Column("date_of_birth", sa.DateTime(), nullable=True),
        sa.Column("enrollment_date", sa.DateTime(), nullable=False),
        sa.Column("last_activity", sa.DateTime(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("notes", sa.String(length=1000), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_plugin_loyalty_customers_tenant_id",
        "plugin_loyalty_customers",
        ["tenant_id"],
    )
    op.create_index(
        "ix_plugin_loyalty_customers_card_number",
        "plugin_loyalty_customers",
        ["card_number"],
        unique=True,
    )
    op.create_index(
        "ix_plugin_loyalty_customers_email",
        "plugin_loyalty_customers",
        ["email"],
    )
    op.create_index(
        "ix_plugin_loyalty_customers_phone",
        "plugin_loyalty_customers",
        ["phone"],
    )

    # Create loyalty_transactions table
    op.create_table(
        "plugin_loyalty_transactions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("tenant_id", sa.String(length=100), nullable=False),
        sa.Column("customer_id", sa.Integer(), nullable=False),
        sa.Column("transaction_type", sa.String(length=20), nullable=False),
        sa.Column("points", sa.Integer(), nullable=False),
        sa.Column("points_before", sa.Integer(), nullable=False),
        sa.Column("points_after", sa.Integer(), nullable=False),
        sa.Column("reference_type", sa.String(length=50), nullable=True),
        sa.Column("reference_id", sa.Integer(), nullable=True),
        sa.Column("amount_spent", sa.Numeric(10, 2), nullable=True),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("expires_at", sa.DateTime(), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["customer_id"],
            ["plugin_loyalty_customers.id"],
        ),
        sa.ForeignKeyConstraint(
            ["created_by"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_plugin_loyalty_transactions_tenant_id",
        "plugin_loyalty_transactions",
        ["tenant_id"],
    )
    op.create_index(
        "ix_plugin_loyalty_transactions_customer_id",
        "plugin_loyalty_transactions",
        ["customer_id"],
    )
    op.create_index(
        "ix_plugin_loyalty_transactions_created_at",
        "plugin_loyalty_transactions",
        ["created_at"],
    )

    # Create loyalty_tiers table
    op.create_table(
        "plugin_loyalty_tiers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("tenant_id", sa.String(length=100), nullable=False),
        sa.Column("tier_name", sa.String(length=50), nullable=False),
        sa.Column("min_points", sa.Integer(), nullable=False),
        sa.Column(
            "points_multiplier", sa.Numeric(3, 2), nullable=False, server_default="1.0"
        ),
        sa.Column(
            "discount_percentage", sa.Numeric(5, 2), nullable=False, server_default="0"
        ),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("color", sa.String(length=20), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_plugin_loyalty_tiers_tenant_id",
        "plugin_loyalty_tiers",
        ["tenant_id"],
    )

    # Create loyalty_rewards table
    op.create_table(
        "plugin_loyalty_rewards",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("tenant_id", sa.String(length=100), nullable=False),
        sa.Column("reward_name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.String(length=1000), nullable=True),
        sa.Column("points_required", sa.Integer(), nullable=False),
        sa.Column("reward_type", sa.String(length=20), nullable=False),
        sa.Column("reward_value", sa.Numeric(10, 2), nullable=True),
        sa.Column("max_redemptions", sa.Integer(), nullable=True),
        sa.Column("redemption_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("valid_from", sa.DateTime(), nullable=True),
        sa.Column("valid_until", sa.DateTime(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_plugin_loyalty_rewards_tenant_id",
        "plugin_loyalty_rewards",
        ["tenant_id"],
    )

    # Create loyalty_campaigns table
    op.create_table(
        "plugin_loyalty_campaigns",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("tenant_id", sa.String(length=100), nullable=False),
        sa.Column("campaign_name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.String(length=1000), nullable=True),
        sa.Column("campaign_type", sa.String(length=20), nullable=False),
        sa.Column("points_multiplier", sa.Numeric(3, 2), nullable=True),
        sa.Column("bonus_points", sa.Integer(), nullable=True),
        sa.Column("start_date", sa.DateTime(), nullable=False),
        sa.Column("end_date", sa.DateTime(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("target_tier", sa.String(length=20), nullable=True),
        sa.Column("min_purchase_amount", sa.Numeric(10, 2), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_plugin_loyalty_campaigns_tenant_id",
        "plugin_loyalty_campaigns",
        ["tenant_id"],
    )
    op.create_index(
        "ix_plugin_loyalty_campaigns_dates",
        "plugin_loyalty_campaigns",
        ["start_date", "end_date"],
    )


def downgrade() -> None:
    """Drop loyalty program tables."""
    op.drop_index(
        "ix_plugin_loyalty_campaigns_dates",
        table_name="plugin_loyalty_campaigns",
    )
    op.drop_index(
        "ix_plugin_loyalty_campaigns_tenant_id",
        table_name="plugin_loyalty_campaigns",
    )
    op.drop_table("plugin_loyalty_campaigns")

    op.drop_index(
        "ix_plugin_loyalty_rewards_tenant_id",
        table_name="plugin_loyalty_rewards",
    )
    op.drop_table("plugin_loyalty_rewards")

    op.drop_index(
        "ix_plugin_loyalty_tiers_tenant_id",
        table_name="plugin_loyalty_tiers",
    )
    op.drop_table("plugin_loyalty_tiers")

    op.drop_index(
        "ix_plugin_loyalty_transactions_created_at",
        table_name="plugin_loyalty_transactions",
    )
    op.drop_index(
        "ix_plugin_loyalty_transactions_customer_id",
        table_name="plugin_loyalty_transactions",
    )
    op.drop_index(
        "ix_plugin_loyalty_transactions_tenant_id",
        table_name="plugin_loyalty_transactions",
    )
    op.drop_table("plugin_loyalty_transactions")

    op.drop_index(
        "ix_plugin_loyalty_customers_phone",
        table_name="plugin_loyalty_customers",
    )
    op.drop_index(
        "ix_plugin_loyalty_customers_email",
        table_name="plugin_loyalty_customers",
    )
    op.drop_index(
        "ix_plugin_loyalty_customers_card_number",
        table_name="plugin_loyalty_customers",
    )
    op.drop_index(
        "ix_plugin_loyalty_customers_tenant_id",
        table_name="plugin_loyalty_customers",
    )
    op.drop_table("plugin_loyalty_customers")

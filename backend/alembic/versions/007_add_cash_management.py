"""Add cash management plugin tables

Revision ID: 007_cash_management
Revises: 006_kitchen_display
Create Date: 2025-11-06

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "007_cash_management"
down_revision: Union[str, None] = "006_kitchen_display"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create cash management tables."""
    # Create cash_registers table
    op.create_table(
        "plugin_cash_registers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("tenant_id", sa.String(length=100), nullable=False),
        sa.Column("register_name", sa.String(length=100), nullable=False),
        sa.Column("register_number", sa.String(length=50), nullable=True),
        sa.Column(
            "current_balance", sa.Numeric(10, 2), nullable=False, server_default="0"
        ),
        sa.Column(
            "starting_float", sa.Numeric(10, 2), nullable=False, server_default="0"
        ),
        sa.Column(
            "status", sa.String(length=20), nullable=False, server_default="closed"
        ),
        sa.Column("opened_at", sa.DateTime(), nullable=True),
        sa.Column("opened_by", sa.Integer(), nullable=True),
        sa.Column("closed_at", sa.DateTime(), nullable=True),
        sa.Column("closed_by", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.ForeignKeyConstraint(
            ["opened_by"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["closed_by"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_plugin_cash_registers_tenant_id",
        "plugin_cash_registers",
        ["tenant_id"],
    )

    # Create cash_transactions table
    op.create_table(
        "plugin_cash_transactions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("tenant_id", sa.String(length=100), nullable=False),
        sa.Column("register_id", sa.Integer(), nullable=False),
        sa.Column("transaction_type", sa.String(length=20), nullable=False),
        sa.Column("amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("balance_before", sa.Numeric(10, 2), nullable=False),
        sa.Column("balance_after", sa.Numeric(10, 2), nullable=False),
        sa.Column("reference_type", sa.String(length=50), nullable=True),
        sa.Column("reference_id", sa.Integer(), nullable=True),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["register_id"],
            ["plugin_cash_registers.id"],
        ),
        sa.ForeignKeyConstraint(
            ["created_by"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_plugin_cash_transactions_tenant_id",
        "plugin_cash_transactions",
        ["tenant_id"],
    )
    op.create_index(
        "ix_plugin_cash_transactions_register_id",
        "plugin_cash_transactions",
        ["register_id"],
    )
    op.create_index(
        "ix_plugin_cash_transactions_created_at",
        "plugin_cash_transactions",
        ["created_at"],
    )

    # Create cash_counts table
    op.create_table(
        "plugin_cash_counts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("tenant_id", sa.String(length=100), nullable=False),
        sa.Column("register_id", sa.Integer(), nullable=False),
        sa.Column("count_type", sa.String(length=20), nullable=False),
        sa.Column("expected_amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("counted_amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("difference", sa.Numeric(10, 2), nullable=False),
        sa.Column("count_time", sa.DateTime(), nullable=False),
        sa.Column("notes", sa.String(length=1000), nullable=True),
        sa.Column("counted_by", sa.Integer(), nullable=True),
        sa.Column("approved_by", sa.Integer(), nullable=True),
        sa.Column("approved_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["register_id"],
            ["plugin_cash_registers.id"],
        ),
        sa.ForeignKeyConstraint(
            ["counted_by"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["approved_by"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_plugin_cash_counts_tenant_id",
        "plugin_cash_counts",
        ["tenant_id"],
    )
    op.create_index(
        "ix_plugin_cash_counts_register_id",
        "plugin_cash_counts",
        ["register_id"],
    )
    op.create_index(
        "ix_plugin_cash_counts_count_time",
        "plugin_cash_counts",
        ["count_time"],
    )

    # Create cash_count_denominations table
    op.create_table(
        "plugin_cash_count_denominations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("tenant_id", sa.String(length=100), nullable=False),
        sa.Column("count_id", sa.Integer(), nullable=False),
        sa.Column("denomination_type", sa.String(length=10), nullable=False),
        sa.Column("denomination_value", sa.Numeric(10, 2), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("total_value", sa.Numeric(10, 2), nullable=False),
        sa.ForeignKeyConstraint(
            ["count_id"],
            ["plugin_cash_counts.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_plugin_cash_count_denominations_tenant_id",
        "plugin_cash_count_denominations",
        ["tenant_id"],
    )
    op.create_index(
        "ix_plugin_cash_count_denominations_count_id",
        "plugin_cash_count_denominations",
        ["count_id"],
    )

    # Create cash_deposits table
    op.create_table(
        "plugin_cash_deposits",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("tenant_id", sa.String(length=100), nullable=False),
        sa.Column("register_id", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Numeric(10, 2), nullable=False),
        sa.Column(
            "deposit_type", sa.String(length=20), nullable=False, server_default="safe"
        ),
        sa.Column("deposit_time", sa.DateTime(), nullable=False),
        sa.Column("deposited_by", sa.Integer(), nullable=True),
        sa.Column("notes", sa.String(length=500), nullable=True),
        sa.ForeignKeyConstraint(
            ["register_id"],
            ["plugin_cash_registers.id"],
        ),
        sa.ForeignKeyConstraint(
            ["deposited_by"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_plugin_cash_deposits_tenant_id",
        "plugin_cash_deposits",
        ["tenant_id"],
    )
    op.create_index(
        "ix_plugin_cash_deposits_register_id",
        "plugin_cash_deposits",
        ["register_id"],
    )

    # Create cash_floats table
    op.create_table(
        "plugin_cash_floats",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("tenant_id", sa.String(length=100), nullable=False),
        sa.Column("register_id", sa.Integer(), nullable=False),
        sa.Column("float_amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("float_date", sa.DateTime(), nullable=False),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["register_id"],
            ["plugin_cash_registers.id"],
        ),
        sa.ForeignKeyConstraint(
            ["created_by"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_plugin_cash_floats_tenant_id",
        "plugin_cash_floats",
        ["tenant_id"],
    )
    op.create_index(
        "ix_plugin_cash_floats_register_id",
        "plugin_cash_floats",
        ["register_id"],
    )


def downgrade() -> None:
    """Drop cash management tables."""
    op.drop_index(
        "ix_plugin_cash_floats_register_id",
        table_name="plugin_cash_floats",
    )
    op.drop_index(
        "ix_plugin_cash_floats_tenant_id",
        table_name="plugin_cash_floats",
    )
    op.drop_table("plugin_cash_floats")

    op.drop_index(
        "ix_plugin_cash_deposits_register_id",
        table_name="plugin_cash_deposits",
    )
    op.drop_index(
        "ix_plugin_cash_deposits_tenant_id",
        table_name="plugin_cash_deposits",
    )
    op.drop_table("plugin_cash_deposits")

    op.drop_index(
        "ix_plugin_cash_count_denominations_count_id",
        table_name="plugin_cash_count_denominations",
    )
    op.drop_index(
        "ix_plugin_cash_count_denominations_tenant_id",
        table_name="plugin_cash_count_denominations",
    )
    op.drop_table("plugin_cash_count_denominations")

    op.drop_index(
        "ix_plugin_cash_counts_count_time",
        table_name="plugin_cash_counts",
    )
    op.drop_index(
        "ix_plugin_cash_counts_register_id",
        table_name="plugin_cash_counts",
    )
    op.drop_index(
        "ix_plugin_cash_counts_tenant_id",
        table_name="plugin_cash_counts",
    )
    op.drop_table("plugin_cash_counts")

    op.drop_index(
        "ix_plugin_cash_transactions_created_at",
        table_name="plugin_cash_transactions",
    )
    op.drop_index(
        "ix_plugin_cash_transactions_register_id",
        table_name="plugin_cash_transactions",
    )
    op.drop_index(
        "ix_plugin_cash_transactions_tenant_id",
        table_name="plugin_cash_transactions",
    )
    op.drop_table("plugin_cash_transactions")

    op.drop_index(
        "ix_plugin_cash_registers_tenant_id",
        table_name="plugin_cash_registers",
    )
    op.drop_table("plugin_cash_registers")

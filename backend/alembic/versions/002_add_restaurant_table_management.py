"""Add restaurant table management plugin tables

Revision ID: 002_restaurant_tables
Revises: 001_plugin_licenses
Create Date: 2025-11-06

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "002_restaurant_tables"
down_revision: Union[str, None] = "001_plugin_licenses"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create restaurant table management tables."""
    # Create tables table
    op.create_table(
        "plugin_restaurant_tables",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("tenant_id", sa.String(length=100), nullable=False),
        sa.Column("table_number", sa.Integer(), nullable=False),
        sa.Column("table_name", sa.String(length=100), nullable=True),
        sa.Column("seats", sa.Integer(), nullable=False, server_default="4"),
        sa.Column("position_x", sa.Integer(), nullable=True),
        sa.Column("position_y", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("notes", sa.String(length=500), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_plugin_restaurant_tables_tenant_id",
        "plugin_restaurant_tables",
        ["tenant_id"],
    )
    op.create_index(
        "ix_plugin_restaurant_tables_table_number",
        "plugin_restaurant_tables",
        ["tenant_id", "table_number"],
    )

    # Create table_status table
    op.create_table(
        "plugin_restaurant_table_status",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("tenant_id", sa.String(length=100), nullable=False),
        sa.Column(
            "table_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "status", sa.String(length=20), nullable=False, server_default="available"
        ),
        sa.Column("current_order_id", sa.Integer(), nullable=True),
        sa.Column("assigned_waiter_id", sa.Integer(), nullable=True),
        sa.Column("occupied_since", sa.DateTime(), nullable=True),
        sa.Column("guests_count", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["table_id"],
            ["plugin_restaurant_tables.id"],
        ),
        sa.ForeignKeyConstraint(
            ["assigned_waiter_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_plugin_restaurant_table_status_tenant_id",
        "plugin_restaurant_table_status",
        ["tenant_id"],
    )
    op.create_index(
        "ix_plugin_restaurant_table_status_table_id",
        "plugin_restaurant_table_status",
        ["table_id"],
    )

    # Create reservations table
    op.create_table(
        "plugin_restaurant_reservations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("tenant_id", sa.String(length=100), nullable=False),
        sa.Column("table_id", sa.Integer(), nullable=False),
        sa.Column("customer_name", sa.String(length=200), nullable=False),
        sa.Column("customer_phone", sa.String(length=50), nullable=True),
        sa.Column("customer_email", sa.String(length=200), nullable=True),
        sa.Column("guests_count", sa.Integer(), nullable=False),
        sa.Column("reservation_time", sa.DateTime(), nullable=False),
        sa.Column(
            "duration_minutes", sa.Integer(), nullable=False, server_default="120"
        ),
        sa.Column(
            "status", sa.String(length=20), nullable=False, server_default="confirmed"
        ),
        sa.Column("notes", sa.String(length=1000), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["table_id"],
            ["plugin_restaurant_tables.id"],
        ),
        sa.ForeignKeyConstraint(
            ["created_by"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_plugin_restaurant_reservations_tenant_id",
        "plugin_restaurant_reservations",
        ["tenant_id"],
    )
    op.create_index(
        "ix_plugin_restaurant_reservations_table_id",
        "plugin_restaurant_reservations",
        ["table_id"],
    )
    op.create_index(
        "ix_plugin_restaurant_reservations_time",
        "plugin_restaurant_reservations",
        ["tenant_id", "reservation_time"],
    )


def downgrade() -> None:
    """Drop restaurant table management tables."""
    op.drop_index(
        "ix_plugin_restaurant_reservations_time",
        table_name="plugin_restaurant_reservations",
    )  # noqa
    op.drop_index(
        "ix_plugin_restaurant_reservations_table_id",
        table_name="plugin_restaurant_reservations",
    )  # noqa
    op.drop_index(
        "ix_plugin_restaurant_reservations_tenant_id",
        table_name="plugin_restaurant_reservations",
    )  # noqa
    op.drop_table("plugin_restaurant_reservations")

    op.drop_index(
        "ix_plugin_restaurant_table_status_table_id",
        table_name="plugin_restaurant_table_status",
    )  # noqa
    op.drop_index(
        "ix_plugin_restaurant_table_status_tenant_id",
        table_name="plugin_restaurant_table_status",
    )  # noqa
    op.drop_table("plugin_restaurant_table_status")

    op.drop_index(
        "ix_plugin_restaurant_tables_table_number",
        table_name="plugin_restaurant_tables",
    )  # noqa
    op.drop_index(
        "ix_plugin_restaurant_tables_tenant_id", table_name="plugin_restaurant_tables"
    )  # noqa
    op.drop_table("plugin_restaurant_tables")

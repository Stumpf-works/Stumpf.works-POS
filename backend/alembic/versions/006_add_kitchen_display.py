"""Add kitchen display plugin tables

Revision ID: 006_kitchen_display
Revises: 005_loyalty_program
Create Date: 2025-11-06

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "006_kitchen_display"
down_revision: Union[str, None] = "005_loyalty_program"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create kitchen display tables."""
    # Create kitchen_stations table
    op.create_table(
        "plugin_kitchen_stations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("tenant_id", sa.String(length=100), nullable=False),
        sa.Column("station_name", sa.String(length=100), nullable=False),
        sa.Column("station_type", sa.String(length=50), nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("color", sa.String(length=20), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_plugin_kitchen_stations_tenant_id",
        "plugin_kitchen_stations",
        ["tenant_id"],
    )

    # Create kitchen_orders table
    op.create_table(
        "plugin_kitchen_orders",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("tenant_id", sa.String(length=100), nullable=False),
        sa.Column("order_number", sa.String(length=50), nullable=False),
        sa.Column("table_number", sa.Integer(), nullable=True),
        sa.Column(
            "order_type", sa.String(length=20), nullable=False, server_default="dine_in"
        ),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="new"),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("received_at", sa.DateTime(), nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("prep_time_minutes", sa.Integer(), nullable=True),
        sa.Column("actual_time_minutes", sa.Integer(), nullable=True),
        sa.Column("assigned_to", sa.Integer(), nullable=True),
        sa.Column("notes", sa.String(length=1000), nullable=True),
        sa.ForeignKeyConstraint(
            ["assigned_to"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_plugin_kitchen_orders_tenant_id",
        "plugin_kitchen_orders",
        ["tenant_id"],
    )
    op.create_index(
        "ix_plugin_kitchen_orders_status",
        "plugin_kitchen_orders",
        ["status"],
    )
    op.create_index(
        "ix_plugin_kitchen_orders_received_at",
        "plugin_kitchen_orders",
        ["received_at"],
    )

    # Create kitchen_order_items table
    op.create_table(
        "plugin_kitchen_order_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("tenant_id", sa.String(length=100), nullable=False),
        sa.Column("order_id", sa.Integer(), nullable=False),
        sa.Column("station_id", sa.Integer(), nullable=True),
        sa.Column("item_name", sa.String(length=200), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False, server_default="1"),
        sa.Column(
            "status", sa.String(length=20), nullable=False, server_default="pending"
        ),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("prep_time_minutes", sa.Integer(), nullable=True),
        sa.Column("special_instructions", sa.String(length=500), nullable=True),
        sa.ForeignKeyConstraint(
            ["order_id"],
            ["plugin_kitchen_orders.id"],
        ),
        sa.ForeignKeyConstraint(
            ["station_id"],
            ["plugin_kitchen_stations.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_plugin_kitchen_order_items_tenant_id",
        "plugin_kitchen_order_items",
        ["tenant_id"],
    )
    op.create_index(
        "ix_plugin_kitchen_order_items_order_id",
        "plugin_kitchen_order_items",
        ["order_id"],
    )
    op.create_index(
        "ix_plugin_kitchen_order_items_station_id",
        "plugin_kitchen_order_items",
        ["station_id"],
    )

    # Create kitchen_timers table
    op.create_table(
        "plugin_kitchen_timers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("tenant_id", sa.String(length=100), nullable=False),
        sa.Column("order_id", sa.Integer(), nullable=False),
        sa.Column("order_item_id", sa.Integer(), nullable=True),
        sa.Column("station_id", sa.Integer(), nullable=True),
        sa.Column("timer_name", sa.String(length=100), nullable=False),
        sa.Column("duration_minutes", sa.Integer(), nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("alerted", sa.Boolean(), nullable=False, server_default="false"),
        sa.ForeignKeyConstraint(
            ["order_id"],
            ["plugin_kitchen_orders.id"],
        ),
        sa.ForeignKeyConstraint(
            ["order_item_id"],
            ["plugin_kitchen_order_items.id"],
        ),
        sa.ForeignKeyConstraint(
            ["station_id"],
            ["plugin_kitchen_stations.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_plugin_kitchen_timers_tenant_id",
        "plugin_kitchen_timers",
        ["tenant_id"],
    )
    op.create_index(
        "ix_plugin_kitchen_timers_order_id",
        "plugin_kitchen_timers",
        ["order_id"],
    )
    op.create_index(
        "ix_plugin_kitchen_timers_expires_at",
        "plugin_kitchen_timers",
        ["expires_at"],
    )

    # Create kitchen_stats table
    op.create_table(
        "plugin_kitchen_stats",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("tenant_id", sa.String(length=100), nullable=False),
        sa.Column("stat_date", sa.DateTime(), nullable=False),
        sa.Column("station_id", sa.Integer(), nullable=True),
        sa.Column("total_orders", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("completed_orders", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("cancelled_orders", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("average_prep_time", sa.Integer(), nullable=True),
        sa.Column("peak_hour", sa.Integer(), nullable=True),
        sa.Column("total_items", sa.Integer(), nullable=False, server_default="0"),
        sa.ForeignKeyConstraint(
            ["station_id"],
            ["plugin_kitchen_stations.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_plugin_kitchen_stats_tenant_id",
        "plugin_kitchen_stats",
        ["tenant_id"],
    )
    op.create_index(
        "ix_plugin_kitchen_stats_date",
        "plugin_kitchen_stats",
        ["stat_date"],
    )


def downgrade() -> None:
    """Drop kitchen display tables."""
    op.drop_index(
        "ix_plugin_kitchen_stats_date",
        table_name="plugin_kitchen_stats",
    )
    op.drop_index(
        "ix_plugin_kitchen_stats_tenant_id",
        table_name="plugin_kitchen_stats",
    )
    op.drop_table("plugin_kitchen_stats")

    op.drop_index(
        "ix_plugin_kitchen_timers_expires_at",
        table_name="plugin_kitchen_timers",
    )
    op.drop_index(
        "ix_plugin_kitchen_timers_order_id",
        table_name="plugin_kitchen_timers",
    )
    op.drop_index(
        "ix_plugin_kitchen_timers_tenant_id",
        table_name="plugin_kitchen_timers",
    )
    op.drop_table("plugin_kitchen_timers")

    op.drop_index(
        "ix_plugin_kitchen_order_items_station_id",
        table_name="plugin_kitchen_order_items",
    )
    op.drop_index(
        "ix_plugin_kitchen_order_items_order_id",
        table_name="plugin_kitchen_order_items",
    )
    op.drop_index(
        "ix_plugin_kitchen_order_items_tenant_id",
        table_name="plugin_kitchen_order_items",
    )
    op.drop_table("plugin_kitchen_order_items")

    op.drop_index(
        "ix_plugin_kitchen_orders_received_at",
        table_name="plugin_kitchen_orders",
    )
    op.drop_index(
        "ix_plugin_kitchen_orders_status",
        table_name="plugin_kitchen_orders",
    )
    op.drop_index(
        "ix_plugin_kitchen_orders_tenant_id",
        table_name="plugin_kitchen_orders",
    )
    op.drop_table("plugin_kitchen_orders")

    op.drop_index(
        "ix_plugin_kitchen_stations_tenant_id",
        table_name="plugin_kitchen_stations",
    )
    op.drop_table("plugin_kitchen_stations")

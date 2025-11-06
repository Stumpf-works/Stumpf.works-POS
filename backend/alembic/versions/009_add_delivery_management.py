"""Add delivery management plugin tables

Revision ID: 009_delivery_management
Revises: 008_bakery_management
Create Date: 2025-11-06

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "009_delivery_management"
down_revision: Union[str, None] = "008_bakery_management"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create delivery management tables."""
    # Create delivery_drivers table
    op.create_table(
        "plugin_delivery_drivers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("tenant_id", sa.String(length=100), nullable=False),
        sa.Column("driver_name", sa.String(length=200), nullable=False),
        sa.Column("driver_phone", sa.String(length=50), nullable=False),
        sa.Column("driver_email", sa.String(length=200), nullable=True),
        sa.Column("employee_id", sa.Integer(), nullable=True),
        sa.Column("vehicle_type", sa.String(length=20), nullable=False),
        sa.Column("vehicle_number", sa.String(length=50), nullable=True),
        sa.Column(
            "status", sa.String(length=20), nullable=False, server_default="offline"
        ),
        sa.Column("current_latitude", sa.Numeric(10, 8), nullable=True),
        sa.Column("current_longitude", sa.Numeric(11, 8), nullable=True),
        sa.Column("last_location_update", sa.DateTime(), nullable=True),
        sa.Column("total_deliveries", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "successful_deliveries", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column("average_rating", sa.Numeric(3, 2), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("shift_start", sa.DateTime(), nullable=True),
        sa.Column("shift_end", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_plugin_delivery_drivers_tenant_id",
        "plugin_delivery_drivers",
        ["tenant_id"],
    )
    op.create_index(
        "ix_plugin_delivery_drivers_status",
        "plugin_delivery_drivers",
        ["status"],
    )

    # Create delivery_orders table
    op.create_table(
        "plugin_delivery_orders",
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
        sa.Column("customer_name", sa.String(length=200), nullable=False),
        sa.Column("customer_phone", sa.String(length=50), nullable=False),
        sa.Column("customer_email", sa.String(length=200), nullable=True),
        sa.Column("delivery_address", sa.Text(), nullable=False),
        sa.Column("delivery_latitude", sa.Numeric(10, 8), nullable=True),
        sa.Column("delivery_longitude", sa.Numeric(11, 8), nullable=True),
        sa.Column("delivery_instructions", sa.Text(), nullable=True),
        sa.Column("pickup_address", sa.Text(), nullable=True),
        sa.Column("pickup_latitude", sa.Numeric(10, 8), nullable=True),
        sa.Column("pickup_longitude", sa.Numeric(11, 8), nullable=True),
        sa.Column("driver_id", sa.Integer(), nullable=True),
        sa.Column(
            "delivery_fee", sa.Numeric(10, 2), nullable=False, server_default="0"
        ),
        sa.Column("tip_amount", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column("total_amount", sa.Numeric(10, 2), nullable=False),
        sa.Column(
            "status", sa.String(length=20), nullable=False, server_default="pending"
        ),
        sa.Column(
            "priority", sa.String(length=20), nullable=False, server_default="normal"
        ),
        sa.Column("scheduled_pickup_time", sa.DateTime(), nullable=True),
        sa.Column("scheduled_delivery_time", sa.DateTime(), nullable=True),
        sa.Column("actual_pickup_time", sa.DateTime(), nullable=True),
        sa.Column("actual_delivery_time", sa.DateTime(), nullable=True),
        sa.Column("estimated_delivery_time", sa.DateTime(), nullable=True),
        sa.Column("external_platform", sa.String(length=50), nullable=True),
        sa.Column("external_order_id", sa.String(length=100), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("cancellation_reason", sa.String(length=500), nullable=True),
        sa.Column("assigned_by", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["driver_id"],
            ["plugin_delivery_drivers.id"],
        ),
        sa.ForeignKeyConstraint(
            ["assigned_by"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_plugin_delivery_orders_tenant_id",
        "plugin_delivery_orders",
        ["tenant_id"],
    )
    op.create_index(
        "ix_plugin_delivery_orders_order_number",
        "plugin_delivery_orders",
        ["order_number"],
    )
    op.create_index(
        "ix_plugin_delivery_orders_status",
        "plugin_delivery_orders",
        ["status"],
    )
    op.create_index(
        "ix_plugin_delivery_orders_driver_id",
        "plugin_delivery_orders",
        ["driver_id"],
    )

    # Create delivery_routes table
    op.create_table(
        "plugin_delivery_routes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("tenant_id", sa.String(length=100), nullable=False),
        sa.Column("driver_id", sa.Integer(), nullable=False),
        sa.Column("route_name", sa.String(length=100), nullable=False),
        sa.Column("route_date", sa.Date(), nullable=False),
        sa.Column("start_time", sa.DateTime(), nullable=True),
        sa.Column("end_time", sa.DateTime(), nullable=True),
        sa.Column("estimated_duration", sa.Integer(), nullable=True),
        sa.Column("actual_duration", sa.Integer(), nullable=True),
        sa.Column("total_distance", sa.Numeric(10, 2), nullable=True),
        sa.Column(
            "status", sa.String(length=20), nullable=False, server_default="planned"
        ),
        sa.Column("order_sequence", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["driver_id"],
            ["plugin_delivery_drivers.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_plugin_delivery_routes_tenant_id",
        "plugin_delivery_routes",
        ["tenant_id"],
    )
    op.create_index(
        "ix_plugin_delivery_routes_driver_id",
        "plugin_delivery_routes",
        ["driver_id"],
    )
    op.create_index(
        "ix_plugin_delivery_routes_route_date",
        "plugin_delivery_routes",
        ["route_date"],
    )

    # Create delivery_route_stops table
    op.create_table(
        "plugin_delivery_route_stops",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("tenant_id", sa.String(length=100), nullable=False),
        sa.Column("route_id", sa.Integer(), nullable=False),
        sa.Column("order_id", sa.Integer(), nullable=False),
        sa.Column("stop_sequence", sa.Integer(), nullable=False),
        sa.Column("stop_type", sa.String(length=20), nullable=False),
        sa.Column("planned_arrival_time", sa.DateTime(), nullable=True),
        sa.Column("actual_arrival_time", sa.DateTime(), nullable=True),
        sa.Column("address", sa.Text(), nullable=False),
        sa.Column("latitude", sa.Numeric(10, 8), nullable=True),
        sa.Column("longitude", sa.Numeric(11, 8), nullable=True),
        sa.Column(
            "status", sa.String(length=20), nullable=False, server_default="pending"
        ),
        sa.Column("notes", sa.String(length=500), nullable=True),
        sa.ForeignKeyConstraint(
            ["route_id"],
            ["plugin_delivery_routes.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_plugin_delivery_route_stops_tenant_id",
        "plugin_delivery_route_stops",
        ["tenant_id"],
    )
    op.create_index(
        "ix_plugin_delivery_route_stops_route_id",
        "plugin_delivery_route_stops",
        ["route_id"],
    )

    # Create delivery_tracking table
    op.create_table(
        "plugin_delivery_tracking",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("tenant_id", sa.String(length=100), nullable=False),
        sa.Column("delivery_order_id", sa.Integer(), nullable=False),
        sa.Column("latitude", sa.Numeric(10, 8), nullable=True),
        sa.Column("longitude", sa.Numeric(11, 8), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("status_message", sa.String(length=500), nullable=True),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("estimated_arrival", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["delivery_order_id"],
            ["plugin_delivery_orders.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_plugin_delivery_tracking_tenant_id",
        "plugin_delivery_tracking",
        ["tenant_id"],
    )
    op.create_index(
        "ix_plugin_delivery_tracking_delivery_order_id",
        "plugin_delivery_tracking",
        ["delivery_order_id"],
    )
    op.create_index(
        "ix_plugin_delivery_tracking_timestamp",
        "plugin_delivery_tracking",
        ["timestamp"],
    )

    # Create delivery_zones table
    op.create_table(
        "plugin_delivery_zones",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("tenant_id", sa.String(length=100), nullable=False),
        sa.Column("zone_name", sa.String(length=100), nullable=False),
        sa.Column("zone_code", sa.String(length=20), nullable=True),
        sa.Column("zone_boundaries", sa.Text(), nullable=True),
        sa.Column(
            "base_delivery_fee", sa.Numeric(10, 2), nullable=False, server_default="0"
        ),
        sa.Column(
            "minimum_order_amount",
            sa.Numeric(10, 2),
            nullable=False,
            server_default="0",
        ),
        sa.Column("free_delivery_threshold", sa.Numeric(10, 2), nullable=True),
        sa.Column(
            "estimated_delivery_time", sa.Integer(), nullable=False, server_default="30"
        ),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("delivery_hours", sa.Text(), nullable=True),
        sa.Column("notes", sa.String(length=500), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_plugin_delivery_zones_tenant_id",
        "plugin_delivery_zones",
        ["tenant_id"],
    )

    # Create delivery_performance table
    op.create_table(
        "plugin_delivery_performance",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("tenant_id", sa.String(length=100), nullable=False),
        sa.Column("performance_date", sa.Date(), nullable=False),
        sa.Column("driver_id", sa.Integer(), nullable=True),
        sa.Column("total_deliveries", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "successful_deliveries", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column(
            "cancelled_deliveries", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column(
            "total_distance", sa.Numeric(10, 2), nullable=False, server_default="0"
        ),
        sa.Column(
            "total_delivery_time", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column("average_delivery_time", sa.Integer(), nullable=True),
        sa.Column(
            "on_time_deliveries", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column("late_deliveries", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_tips", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column("customer_rating", sa.Numeric(3, 2), nullable=True),
        sa.ForeignKeyConstraint(
            ["driver_id"],
            ["plugin_delivery_drivers.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_plugin_delivery_performance_tenant_id",
        "plugin_delivery_performance",
        ["tenant_id"],
    )
    op.create_index(
        "ix_plugin_delivery_performance_performance_date",
        "plugin_delivery_performance",
        ["performance_date"],
    )
    op.create_index(
        "ix_plugin_delivery_performance_driver_id",
        "plugin_delivery_performance",
        ["driver_id"],
    )


def downgrade() -> None:
    """Drop delivery management tables."""
    op.drop_index(
        "ix_plugin_delivery_performance_driver_id",
        table_name="plugin_delivery_performance",
    )
    op.drop_index(
        "ix_plugin_delivery_performance_performance_date",
        table_name="plugin_delivery_performance",
    )
    op.drop_index(
        "ix_plugin_delivery_performance_tenant_id",
        table_name="plugin_delivery_performance",
    )
    op.drop_table("plugin_delivery_performance")

    op.drop_index(
        "ix_plugin_delivery_zones_tenant_id",
        table_name="plugin_delivery_zones",
    )
    op.drop_table("plugin_delivery_zones")

    op.drop_index(
        "ix_plugin_delivery_tracking_timestamp",
        table_name="plugin_delivery_tracking",
    )
    op.drop_index(
        "ix_plugin_delivery_tracking_delivery_order_id",
        table_name="plugin_delivery_tracking",
    )
    op.drop_index(
        "ix_plugin_delivery_tracking_tenant_id",
        table_name="plugin_delivery_tracking",
    )
    op.drop_table("plugin_delivery_tracking")

    op.drop_index(
        "ix_plugin_delivery_route_stops_route_id",
        table_name="plugin_delivery_route_stops",
    )
    op.drop_index(
        "ix_plugin_delivery_route_stops_tenant_id",
        table_name="plugin_delivery_route_stops",
    )
    op.drop_table("plugin_delivery_route_stops")

    op.drop_index(
        "ix_plugin_delivery_routes_route_date",
        table_name="plugin_delivery_routes",
    )
    op.drop_index(
        "ix_plugin_delivery_routes_driver_id",
        table_name="plugin_delivery_routes",
    )
    op.drop_index(
        "ix_plugin_delivery_routes_tenant_id",
        table_name="plugin_delivery_routes",
    )
    op.drop_table("plugin_delivery_routes")

    op.drop_index(
        "ix_plugin_delivery_orders_driver_id",
        table_name="plugin_delivery_orders",
    )
    op.drop_index(
        "ix_plugin_delivery_orders_status",
        table_name="plugin_delivery_orders",
    )
    op.drop_index(
        "ix_plugin_delivery_orders_order_number",
        table_name="plugin_delivery_orders",
    )
    op.drop_index(
        "ix_plugin_delivery_orders_tenant_id",
        table_name="plugin_delivery_orders",
    )
    op.drop_table("plugin_delivery_orders")

    op.drop_index(
        "ix_plugin_delivery_drivers_status",
        table_name="plugin_delivery_drivers",
    )
    op.drop_index(
        "ix_plugin_delivery_drivers_tenant_id",
        table_name="plugin_delivery_drivers",
    )
    op.drop_table("plugin_delivery_drivers")

"""Add inventory management plugin tables

Revision ID: 003_inventory_management
Revises: 002_restaurant_tables
Create Date: 2025-11-06

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "003_inventory_management"
down_revision: Union[str, None] = "002_restaurant_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create inventory management tables."""
    # Create suppliers table
    op.create_table(
        "plugin_inventory_suppliers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("tenant_id", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=True),
        sa.Column("contact_person", sa.String(length=200), nullable=True),
        sa.Column("email", sa.String(length=200), nullable=True),
        sa.Column("phone", sa.String(length=50), nullable=True),
        sa.Column("address", sa.String(length=500), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("notes", sa.String(length=1000), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_plugin_inventory_suppliers_tenant_id",
        "plugin_inventory_suppliers",
        ["tenant_id"],
    )

    # Create stock_levels table
    op.create_table(
        "plugin_inventory_stock_levels",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("tenant_id", sa.String(length=100), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column("min_level", sa.Numeric(10, 2), nullable=True),
        sa.Column("max_level", sa.Numeric(10, 2), nullable=True),
        sa.Column("reorder_point", sa.Numeric(10, 2), nullable=True),
        sa.Column("reorder_quantity", sa.Numeric(10, 2), nullable=True),
        sa.Column("unit_cost", sa.Numeric(10, 2), nullable=True),
        sa.Column("supplier_id", sa.Integer(), nullable=True),
        sa.Column("barcode", sa.String(length=100), nullable=True),
        sa.Column("location", sa.String(length=200), nullable=True),
        sa.ForeignKeyConstraint(
            ["supplier_id"],
            ["plugin_inventory_suppliers.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_plugin_inventory_stock_levels_tenant_id",
        "plugin_inventory_stock_levels",
        ["tenant_id"],
    )
    op.create_index(
        "ix_plugin_inventory_stock_levels_product_id",
        "plugin_inventory_stock_levels",
        ["tenant_id", "product_id"],
        unique=True,
    )

    # Create stock_movements table
    op.create_table(
        "plugin_inventory_movements",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("tenant_id", sa.String(length=100), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("movement_type", sa.String(length=20), nullable=False),
        sa.Column("quantity", sa.Numeric(10, 2), nullable=False),
        sa.Column("quantity_before", sa.Numeric(10, 2), nullable=False),
        sa.Column("quantity_after", sa.Numeric(10, 2), nullable=False),
        sa.Column("unit_cost", sa.Numeric(10, 2), nullable=True),
        sa.Column("reference_type", sa.String(length=50), nullable=True),
        sa.Column("reference_id", sa.Integer(), nullable=True),
        sa.Column("notes", sa.String(length=1000), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["created_by"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_plugin_inventory_movements_tenant_id",
        "plugin_inventory_movements",
        ["tenant_id"],
    )
    op.create_index(
        "ix_plugin_inventory_movements_product_id",
        "plugin_inventory_movements",
        ["product_id"],
    )
    op.create_index(
        "ix_plugin_inventory_movements_created_at",
        "plugin_inventory_movements",
        ["created_at"],
    )

    # Create purchase_orders table
    op.create_table(
        "plugin_inventory_purchase_orders",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("tenant_id", sa.String(length=100), nullable=False),
        sa.Column("order_number", sa.String(length=50), nullable=False, unique=True),
        sa.Column("supplier_id", sa.Integer(), nullable=False),
        sa.Column(
            "status", sa.String(length=20), nullable=False, server_default="draft"
        ),
        sa.Column("order_date", sa.DateTime(), nullable=False),
        sa.Column("expected_delivery", sa.DateTime(), nullable=True),
        sa.Column("actual_delivery", sa.DateTime(), nullable=True),
        sa.Column(
            "total_amount", sa.Numeric(10, 2), nullable=False, server_default="0"
        ),
        sa.Column("notes", sa.String(length=1000), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["supplier_id"],
            ["plugin_inventory_suppliers.id"],
        ),
        sa.ForeignKeyConstraint(
            ["created_by"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_plugin_inventory_purchase_orders_tenant_id",
        "plugin_inventory_purchase_orders",
        ["tenant_id"],
    )
    op.create_index(
        "ix_plugin_inventory_purchase_orders_order_number",
        "plugin_inventory_purchase_orders",
        ["order_number"],
        unique=True,
    )

    # Create purchase_order_items table
    op.create_table(
        "plugin_inventory_purchase_order_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("tenant_id", sa.String(length=100), nullable=False),
        sa.Column("purchase_order_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Numeric(10, 2), nullable=False),
        sa.Column("unit_cost", sa.Numeric(10, 2), nullable=False),
        sa.Column("total_cost", sa.Numeric(10, 2), nullable=False),
        sa.Column(
            "received_quantity", sa.Numeric(10, 2), nullable=False, server_default="0"
        ),
        sa.ForeignKeyConstraint(
            ["purchase_order_id"],
            ["plugin_inventory_purchase_orders.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_plugin_inventory_purchase_order_items_tenant_id",
        "plugin_inventory_purchase_order_items",
        ["tenant_id"],
    )
    op.create_index(
        "ix_plugin_inventory_purchase_order_items_po_id",
        "plugin_inventory_purchase_order_items",
        ["purchase_order_id"],
    )

    # Create inventory_counts table
    op.create_table(
        "plugin_inventory_counts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("tenant_id", sa.String(length=100), nullable=False),
        sa.Column("count_number", sa.String(length=50), nullable=False, unique=True),
        sa.Column(
            "status", sa.String(length=20), nullable=False, server_default="in_progress"
        ),
        sa.Column("start_time", sa.DateTime(), nullable=False),
        sa.Column("end_time", sa.DateTime(), nullable=True),
        sa.Column("notes", sa.String(length=1000), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["created_by"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_plugin_inventory_counts_tenant_id",
        "plugin_inventory_counts",
        ["tenant_id"],
    )
    op.create_index(
        "ix_plugin_inventory_counts_count_number",
        "plugin_inventory_counts",
        ["count_number"],
        unique=True,
    )

    # Create inventory_count_items table
    op.create_table(
        "plugin_inventory_count_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("tenant_id", sa.String(length=100), nullable=False),
        sa.Column("count_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("expected_quantity", sa.Numeric(10, 2), nullable=False),
        sa.Column("counted_quantity", sa.Numeric(10, 2), nullable=False),
        sa.Column("difference", sa.Numeric(10, 2), nullable=False),
        sa.Column("notes", sa.String(length=500), nullable=True),
        sa.ForeignKeyConstraint(
            ["count_id"],
            ["plugin_inventory_counts.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_plugin_inventory_count_items_tenant_id",
        "plugin_inventory_count_items",
        ["tenant_id"],
    )
    op.create_index(
        "ix_plugin_inventory_count_items_count_id",
        "plugin_inventory_count_items",
        ["count_id"],
    )


def downgrade() -> None:
    """Drop inventory management tables."""
    op.drop_index(
        "ix_plugin_inventory_count_items_count_id",
        table_name="plugin_inventory_count_items",
    )
    op.drop_index(
        "ix_plugin_inventory_count_items_tenant_id",
        table_name="plugin_inventory_count_items",
    )
    op.drop_table("plugin_inventory_count_items")

    op.drop_index(
        "ix_plugin_inventory_counts_count_number",
        table_name="plugin_inventory_counts",
    )
    op.drop_index(
        "ix_plugin_inventory_counts_tenant_id",
        table_name="plugin_inventory_counts",
    )
    op.drop_table("plugin_inventory_counts")

    op.drop_index(
        "ix_plugin_inventory_purchase_order_items_po_id",
        table_name="plugin_inventory_purchase_order_items",
    )
    op.drop_index(
        "ix_plugin_inventory_purchase_order_items_tenant_id",
        table_name="plugin_inventory_purchase_order_items",
    )
    op.drop_table("plugin_inventory_purchase_order_items")

    op.drop_index(
        "ix_plugin_inventory_purchase_orders_order_number",
        table_name="plugin_inventory_purchase_orders",
    )
    op.drop_index(
        "ix_plugin_inventory_purchase_orders_tenant_id",
        table_name="plugin_inventory_purchase_orders",
    )
    op.drop_table("plugin_inventory_purchase_orders")

    op.drop_index(
        "ix_plugin_inventory_movements_created_at",
        table_name="plugin_inventory_movements",
    )
    op.drop_index(
        "ix_plugin_inventory_movements_product_id",
        table_name="plugin_inventory_movements",
    )
    op.drop_index(
        "ix_plugin_inventory_movements_tenant_id",
        table_name="plugin_inventory_movements",
    )
    op.drop_table("plugin_inventory_movements")

    op.drop_index(
        "ix_plugin_inventory_stock_levels_product_id",
        table_name="plugin_inventory_stock_levels",
    )
    op.drop_index(
        "ix_plugin_inventory_stock_levels_tenant_id",
        table_name="plugin_inventory_stock_levels",
    )
    op.drop_table("plugin_inventory_stock_levels")

    op.drop_index(
        "ix_plugin_inventory_suppliers_tenant_id",
        table_name="plugin_inventory_suppliers",
    )
    op.drop_table("plugin_inventory_suppliers")

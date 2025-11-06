"""Add bakery management plugin tables

Revision ID: 008_bakery_management
Revises: 007_cash_management
Create Date: 2025-11-06

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "008_bakery_management"
down_revision: Union[str, None] = "007_cash_management"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create bakery management tables."""
    # Create recipes table
    op.create_table(
        "plugin_bakery_recipes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("tenant_id", sa.String(length=100), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("recipe_name", sa.String(length=200), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=True),
        sa.Column("preparation_time", sa.Integer(), nullable=True),
        sa.Column("baking_time", sa.Integer(), nullable=True),
        sa.Column("baking_temperature", sa.Integer(), nullable=True),
        sa.Column("yield_quantity", sa.Numeric(10, 2), nullable=False),
        sa.Column("instructions", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_plugin_bakery_recipes_tenant_id",
        "plugin_bakery_recipes",
        ["tenant_id"],
    )
    op.create_index(
        "ix_plugin_bakery_recipes_product_id",
        "plugin_bakery_recipes",
        ["product_id"],
    )

    # Create recipe_ingredients table
    op.create_table(
        "plugin_bakery_recipe_ingredients",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("tenant_id", sa.String(length=100), nullable=False),
        sa.Column("recipe_id", sa.Integer(), nullable=False),
        sa.Column("ingredient_name", sa.String(length=200), nullable=False),
        sa.Column("quantity", sa.Numeric(10, 3), nullable=False),
        sa.Column("unit", sa.String(length=20), nullable=False),
        sa.Column("ingredient_type", sa.String(length=50), nullable=True),
        sa.Column("notes", sa.String(length=500), nullable=True),
        sa.ForeignKeyConstraint(
            ["recipe_id"],
            ["plugin_bakery_recipes.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_plugin_bakery_recipe_ingredients_tenant_id",
        "plugin_bakery_recipe_ingredients",
        ["tenant_id"],
    )
    op.create_index(
        "ix_plugin_bakery_recipe_ingredients_recipe_id",
        "plugin_bakery_recipe_ingredients",
        ["recipe_id"],
    )

    # Create production_plans table
    op.create_table(
        "plugin_bakery_production_plans",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("tenant_id", sa.String(length=100), nullable=False),
        sa.Column("plan_date", sa.Date(), nullable=False),
        sa.Column("recipe_id", sa.Integer(), nullable=False),
        sa.Column("planned_quantity", sa.Numeric(10, 2), nullable=False),
        sa.Column("produced_quantity", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="planned"),
        sa.Column("start_time", sa.DateTime(), nullable=True),
        sa.Column("end_time", sa.DateTime(), nullable=True),
        sa.Column("notes", sa.String(length=1000), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["recipe_id"],
            ["plugin_bakery_recipes.id"],
        ),
        sa.ForeignKeyConstraint(
            ["created_by"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_plugin_bakery_production_plans_tenant_id",
        "plugin_bakery_production_plans",
        ["tenant_id"],
    )
    op.create_index(
        "ix_plugin_bakery_production_plans_plan_date",
        "plugin_bakery_production_plans",
        ["plan_date"],
    )

    # Create production_batches table
    op.create_table(
        "plugin_bakery_production_batches",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("tenant_id", sa.String(length=100), nullable=False),
        sa.Column("plan_id", sa.Integer(), nullable=True),
        sa.Column("recipe_id", sa.Integer(), nullable=False),
        sa.Column("batch_number", sa.String(length=50), nullable=False, unique=True),
        sa.Column("production_date", sa.DateTime(), nullable=False),
        sa.Column("quantity_produced", sa.Numeric(10, 2), nullable=False),
        sa.Column("best_before_date", sa.Date(), nullable=True),
        sa.Column("batch_status", sa.String(length=20), nullable=False, server_default="fresh"),
        sa.Column("notes", sa.String(length=500), nullable=True),
        sa.Column("produced_by", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["plan_id"],
            ["plugin_bakery_production_plans.id"],
        ),
        sa.ForeignKeyConstraint(
            ["recipe_id"],
            ["plugin_bakery_recipes.id"],
        ),
        sa.ForeignKeyConstraint(
            ["produced_by"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_plugin_bakery_production_batches_tenant_id",
        "plugin_bakery_production_batches",
        ["tenant_id"],
    )
    op.create_index(
        "ix_plugin_bakery_production_batches_batch_number",
        "plugin_bakery_production_batches",
        ["batch_number"],
        unique=True,
    )
    op.create_index(
        "ix_plugin_bakery_production_batches_best_before",
        "plugin_bakery_production_batches",
        ["best_before_date"],
    )

    # Create freshness_tracking table
    op.create_table(
        "plugin_bakery_freshness_tracking",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("tenant_id", sa.String(length=100), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("batch_id", sa.Integer(), nullable=True),
        sa.Column("production_date", sa.Date(), nullable=False),
        sa.Column("best_before_date", sa.Date(), nullable=False),
        sa.Column("current_quantity", sa.Numeric(10, 2), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="fresh"),
        sa.Column("location", sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(
            ["batch_id"],
            ["plugin_bakery_production_batches.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_plugin_bakery_freshness_tracking_tenant_id",
        "plugin_bakery_freshness_tracking",
        ["tenant_id"],
    )
    op.create_index(
        "ix_plugin_bakery_freshness_tracking_best_before",
        "plugin_bakery_freshness_tracking",
        ["best_before_date"],
    )

    # Create waste_tracking table
    op.create_table(
        "plugin_bakery_waste_tracking",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("tenant_id", sa.String(length=100), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("batch_id", sa.Integer(), nullable=True),
        sa.Column("waste_type", sa.String(length=20), nullable=False),
        sa.Column("quantity", sa.Numeric(10, 2), nullable=False),
        sa.Column("waste_date", sa.DateTime(), nullable=False),
        sa.Column("reason", sa.String(length=500), nullable=True),
        sa.Column("cost_impact", sa.Numeric(10, 2), nullable=True),
        sa.Column("recorded_by", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["batch_id"],
            ["plugin_bakery_production_batches.id"],
        ),
        sa.ForeignKeyConstraint(
            ["recorded_by"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_plugin_bakery_waste_tracking_tenant_id",
        "plugin_bakery_waste_tracking",
        ["tenant_id"],
    )
    op.create_index(
        "ix_plugin_bakery_waste_tracking_waste_date",
        "plugin_bakery_waste_tracking",
        ["waste_date"],
    )

    # Create baking_sheets table
    op.create_table(
        "plugin_bakery_baking_sheets",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("tenant_id", sa.String(length=100), nullable=False),
        sa.Column("sheet_number", sa.String(length=50), nullable=False, unique=True),
        sa.Column("plan_date", sa.Date(), nullable=False),
        sa.Column("generated_at", sa.DateTime(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column("notes", sa.String(length=1000), nullable=True),
        sa.Column("generated_by", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["generated_by"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_plugin_bakery_baking_sheets_tenant_id",
        "plugin_bakery_baking_sheets",
        ["tenant_id"],
    )
    op.create_index(
        "ix_plugin_bakery_baking_sheets_sheet_number",
        "plugin_bakery_baking_sheets",
        ["sheet_number"],
        unique=True,
    )


def downgrade() -> None:
    """Drop bakery management tables."""
    op.drop_index(
        "ix_plugin_bakery_baking_sheets_sheet_number",
        table_name="plugin_bakery_baking_sheets",
    )
    op.drop_index(
        "ix_plugin_bakery_baking_sheets_tenant_id",
        table_name="plugin_bakery_baking_sheets",
    )
    op.drop_table("plugin_bakery_baking_sheets")

    op.drop_index(
        "ix_plugin_bakery_waste_tracking_waste_date",
        table_name="plugin_bakery_waste_tracking",
    )
    op.drop_index(
        "ix_plugin_bakery_waste_tracking_tenant_id",
        table_name="plugin_bakery_waste_tracking",
    )
    op.drop_table("plugin_bakery_waste_tracking")

    op.drop_index(
        "ix_plugin_bakery_freshness_tracking_best_before",
        table_name="plugin_bakery_freshness_tracking",
    )
    op.drop_index(
        "ix_plugin_bakery_freshness_tracking_tenant_id",
        table_name="plugin_bakery_freshness_tracking",
    )
    op.drop_table("plugin_bakery_freshness_tracking")

    op.drop_index(
        "ix_plugin_bakery_production_batches_best_before",
        table_name="plugin_bakery_production_batches",
    )
    op.drop_index(
        "ix_plugin_bakery_production_batches_batch_number",
        table_name="plugin_bakery_production_batches",
    )
    op.drop_index(
        "ix_plugin_bakery_production_batches_tenant_id",
        table_name="plugin_bakery_production_batches",
    )
    op.drop_table("plugin_bakery_production_batches")

    op.drop_index(
        "ix_plugin_bakery_production_plans_plan_date",
        table_name="plugin_bakery_production_plans",
    )
    op.drop_index(
        "ix_plugin_bakery_production_plans_tenant_id",
        table_name="plugin_bakery_production_plans",
    )
    op.drop_table("plugin_bakery_production_plans")

    op.drop_index(
        "ix_plugin_bakery_recipe_ingredients_recipe_id",
        table_name="plugin_bakery_recipe_ingredients",
    )
    op.drop_index(
        "ix_plugin_bakery_recipe_ingredients_tenant_id",
        table_name="plugin_bakery_recipe_ingredients",
    )
    op.drop_table("plugin_bakery_recipe_ingredients")

    op.drop_index(
        "ix_plugin_bakery_recipes_product_id",
        table_name="plugin_bakery_recipes",
    )
    op.drop_index(
        "ix_plugin_bakery_recipes_tenant_id",
        table_name="plugin_bakery_recipes",
    )
    op.drop_table("plugin_bakery_recipes")

"""Add advanced analytics plugin tables

Revision ID: 010_advanced_analytics
Revises: 009_delivery_management
Create Date: 2025-11-06

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "010_advanced_analytics"
down_revision: Union[str, None] = "009_delivery_management"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create advanced analytics tables."""
    # Create analytics_reports table
    op.create_table(
        "plugin_analytics_reports",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("tenant_id", sa.String(length=100), nullable=False),
        sa.Column("report_name", sa.String(length=200), nullable=False),
        sa.Column("report_type", sa.String(length=50), nullable=False),
        sa.Column("report_category", sa.String(length=50), nullable=True),
        sa.Column("report_config", sa.Text(), nullable=True),
        sa.Column("filters", sa.Text(), nullable=True),
        sa.Column("grouping", sa.String(length=100), nullable=True),
        sa.Column("metrics", sa.Text(), nullable=True),
        sa.Column("is_scheduled", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("schedule_frequency", sa.String(length=20), nullable=True),
        sa.Column("schedule_time", sa.String(length=10), nullable=True),
        sa.Column("last_run", sa.DateTime(), nullable=True),
        sa.Column("next_run", sa.DateTime(), nullable=True),
        sa.Column("email_recipients", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["created_by"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_plugin_analytics_reports_tenant_id",
        "plugin_analytics_reports",
        ["tenant_id"],
    )
    op.create_index(
        "ix_plugin_analytics_reports_report_type",
        "plugin_analytics_reports",
        ["report_type"],
    )

    # Create analytics_report_executions table
    op.create_table(
        "plugin_analytics_report_executions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("tenant_id", sa.String(length=100), nullable=False),
        sa.Column("report_id", sa.Integer(), nullable=False),
        sa.Column("execution_time", sa.DateTime(), nullable=False),
        sa.Column(
            "execution_status",
            sa.String(length=20),
            nullable=False,
            server_default="success",
        ),
        sa.Column("date_from", sa.Date(), nullable=True),
        sa.Column("date_to", sa.Date(), nullable=True),
        sa.Column("result_data", sa.Text(), nullable=True),
        sa.Column("record_count", sa.Integer(), nullable=True),
        sa.Column("execution_duration", sa.Integer(), nullable=True),
        sa.Column("export_format", sa.String(length=20), nullable=True),
        sa.Column("export_file_path", sa.String(length=500), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("executed_by", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["report_id"],
            ["plugin_analytics_reports.id"],
        ),
        sa.ForeignKeyConstraint(
            ["executed_by"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_plugin_analytics_report_executions_tenant_id",
        "plugin_analytics_report_executions",
        ["tenant_id"],
    )
    op.create_index(
        "ix_plugin_analytics_report_executions_report_id",
        "plugin_analytics_report_executions",
        ["report_id"],
    )
    op.create_index(
        "ix_plugin_analytics_report_executions_execution_time",
        "plugin_analytics_report_executions",
        ["execution_time"],
    )

    # Create sales_metrics table
    op.create_table(
        "plugin_analytics_sales_metrics",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("tenant_id", sa.String(length=100), nullable=False),
        sa.Column("metric_date", sa.Date(), nullable=False),
        sa.Column("total_sales", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("total_orders", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "average_order_value", sa.Numeric(10, 2), nullable=False, server_default="0"
        ),
        sa.Column(
            "dine_in_sales", sa.Numeric(10, 2), nullable=False, server_default="0"
        ),
        sa.Column(
            "takeaway_sales", sa.Numeric(10, 2), nullable=False, server_default="0"
        ),
        sa.Column(
            "delivery_sales", sa.Numeric(10, 2), nullable=False, server_default="0"
        ),
        sa.Column("cash_sales", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column("card_sales", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column(
            "digital_wallet_sales",
            sa.Numeric(10, 2),
            nullable=False,
            server_default="0",
        ),
        sa.Column("total_customers", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("new_customers", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "returning_customers", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column(
            "total_discounts", sa.Numeric(10, 2), nullable=False, server_default="0"
        ),
        sa.Column(
            "total_refunds", sa.Numeric(10, 2), nullable=False, server_default="0"
        ),
        sa.Column("total_tax", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column("peak_hour_start", sa.String(length=5), nullable=True),
        sa.Column("peak_hour_end", sa.String(length=5), nullable=True),
        sa.Column("peak_hour_sales", sa.Numeric(10, 2), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_plugin_analytics_sales_metrics_tenant_id",
        "plugin_analytics_sales_metrics",
        ["tenant_id"],
    )
    op.create_index(
        "ix_plugin_analytics_sales_metrics_metric_date",
        "plugin_analytics_sales_metrics",
        ["metric_date"],
    )

    # Create product_metrics table
    op.create_table(
        "plugin_analytics_product_metrics",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("tenant_id", sa.String(length=100), nullable=False),
        sa.Column("metric_date", sa.Date(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("quantity_sold", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "total_revenue", sa.Numeric(10, 2), nullable=False, server_default="0"
        ),
        sa.Column(
            "average_price", sa.Numeric(10, 2), nullable=False, server_default="0"
        ),
        sa.Column("profit_margin", sa.Numeric(10, 2), nullable=True),
        sa.Column("cost_of_goods", sa.Numeric(10, 2), nullable=True),
        sa.Column("sales_rank", sa.Integer(), nullable=True),
        sa.Column("revenue_rank", sa.Integer(), nullable=True),
        sa.Column("trend_direction", sa.String(length=20), nullable=True),
        sa.Column("trend_percentage", sa.Numeric(5, 2), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_plugin_analytics_product_metrics_tenant_id",
        "plugin_analytics_product_metrics",
        ["tenant_id"],
    )
    op.create_index(
        "ix_plugin_analytics_product_metrics_metric_date",
        "plugin_analytics_product_metrics",
        ["metric_date"],
    )
    op.create_index(
        "ix_plugin_analytics_product_metrics_product_id",
        "plugin_analytics_product_metrics",
        ["product_id"],
    )

    # Create customer_metrics table
    op.create_table(
        "plugin_analytics_customer_metrics",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("tenant_id", sa.String(length=100), nullable=False),
        sa.Column("metric_date", sa.Date(), nullable=False),
        sa.Column("customer_id", sa.Integer(), nullable=True),
        sa.Column("total_spent", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column("order_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "average_order_value", sa.Numeric(10, 2), nullable=False, server_default="0"
        ),
        sa.Column("lifetime_value", sa.Numeric(12, 2), nullable=True),
        sa.Column("visit_frequency", sa.Numeric(5, 2), nullable=True),
        sa.Column("days_since_last_visit", sa.Integer(), nullable=True),
        sa.Column("customer_segment", sa.String(length=20), nullable=True),
        sa.Column("loyalty_tier", sa.String(length=20), nullable=True),
        sa.Column("preferred_payment_method", sa.String(length=20), nullable=True),
        sa.Column("preferred_order_type", sa.String(length=20), nullable=True),
        sa.Column("favorite_category", sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_plugin_analytics_customer_metrics_tenant_id",
        "plugin_analytics_customer_metrics",
        ["tenant_id"],
    )
    op.create_index(
        "ix_plugin_analytics_customer_metrics_metric_date",
        "plugin_analytics_customer_metrics",
        ["metric_date"],
    )
    op.create_index(
        "ix_plugin_analytics_customer_metrics_customer_id",
        "plugin_analytics_customer_metrics",
        ["customer_id"],
    )

    # Create revenue_forecast table
    op.create_table(
        "plugin_analytics_revenue_forecast",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("tenant_id", sa.String(length=100), nullable=False),
        sa.Column("forecast_date", sa.Date(), nullable=False),
        sa.Column("forecast_type", sa.String(length=20), nullable=False),
        sa.Column("forecasted_revenue", sa.Numeric(12, 2), nullable=False),
        sa.Column("confidence_level", sa.Numeric(3, 2), nullable=True),
        sa.Column("actual_revenue", sa.Numeric(12, 2), nullable=True),
        sa.Column("variance_amount", sa.Numeric(12, 2), nullable=True),
        sa.Column("variance_percentage", sa.Numeric(5, 2), nullable=True),
        sa.Column("model_version", sa.String(length=50), nullable=True),
        sa.Column("forecast_generated_at", sa.DateTime(), nullable=False),
        sa.Column("generated_by", sa.Integer(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["generated_by"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_plugin_analytics_revenue_forecast_tenant_id",
        "plugin_analytics_revenue_forecast",
        ["tenant_id"],
    )
    op.create_index(
        "ix_plugin_analytics_revenue_forecast_forecast_date",
        "plugin_analytics_revenue_forecast",
        ["forecast_date"],
    )

    # Create analytics_dashboards table
    op.create_table(
        "plugin_analytics_dashboards",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("tenant_id", sa.String(length=100), nullable=False),
        sa.Column("dashboard_name", sa.String(length=200), nullable=False),
        sa.Column("dashboard_type", sa.String(length=50), nullable=False),
        sa.Column("layout_config", sa.Text(), nullable=True),
        sa.Column("widgets", sa.Text(), nullable=True),
        sa.Column("is_public", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("shared_with_roles", sa.Text(), nullable=True),
        sa.Column("auto_refresh", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column(
            "refresh_interval", sa.Integer(), nullable=True, server_default="300"
        ),
        sa.Column("is_default", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("display_order", sa.Integer(), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.ForeignKeyConstraint(
            ["created_by"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_plugin_analytics_dashboards_tenant_id",
        "plugin_analytics_dashboards",
        ["tenant_id"],
    )

    # Create analytics_data_exports table
    op.create_table(
        "plugin_analytics_data_exports",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("tenant_id", sa.String(length=100), nullable=False),
        sa.Column("export_name", sa.String(length=200), nullable=False),
        sa.Column("export_type", sa.String(length=50), nullable=False),
        sa.Column("data_source", sa.String(length=100), nullable=True),
        sa.Column("export_format", sa.String(length=20), nullable=False),
        sa.Column("date_range_from", sa.Date(), nullable=True),
        sa.Column("date_range_to", sa.Date(), nullable=True),
        sa.Column("file_path", sa.String(length=500), nullable=True),
        sa.Column("file_size", sa.Integer(), nullable=True),
        sa.Column(
            "export_status",
            sa.String(length=20),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("export_started_at", sa.DateTime(), nullable=True),
        sa.Column("export_completed_at", sa.DateTime(), nullable=True),
        sa.Column("row_count", sa.Integer(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("requested_by", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["requested_by"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_plugin_analytics_data_exports_tenant_id",
        "plugin_analytics_data_exports",
        ["tenant_id"],
    )
    op.create_index(
        "ix_plugin_analytics_data_exports_export_status",
        "plugin_analytics_data_exports",
        ["export_status"],
    )


def downgrade() -> None:
    """Drop advanced analytics tables."""
    op.drop_index(
        "ix_plugin_analytics_data_exports_export_status",
        table_name="plugin_analytics_data_exports",
    )
    op.drop_index(
        "ix_plugin_analytics_data_exports_tenant_id",
        table_name="plugin_analytics_data_exports",
    )
    op.drop_table("plugin_analytics_data_exports")

    op.drop_index(
        "ix_plugin_analytics_dashboards_tenant_id",
        table_name="plugin_analytics_dashboards",
    )
    op.drop_table("plugin_analytics_dashboards")

    op.drop_index(
        "ix_plugin_analytics_revenue_forecast_forecast_date",
        table_name="plugin_analytics_revenue_forecast",
    )
    op.drop_index(
        "ix_plugin_analytics_revenue_forecast_tenant_id",
        table_name="plugin_analytics_revenue_forecast",
    )
    op.drop_table("plugin_analytics_revenue_forecast")

    op.drop_index(
        "ix_plugin_analytics_customer_metrics_customer_id",
        table_name="plugin_analytics_customer_metrics",
    )
    op.drop_index(
        "ix_plugin_analytics_customer_metrics_metric_date",
        table_name="plugin_analytics_customer_metrics",
    )
    op.drop_index(
        "ix_plugin_analytics_customer_metrics_tenant_id",
        table_name="plugin_analytics_customer_metrics",
    )
    op.drop_table("plugin_analytics_customer_metrics")

    op.drop_index(
        "ix_plugin_analytics_product_metrics_product_id",
        table_name="plugin_analytics_product_metrics",
    )
    op.drop_index(
        "ix_plugin_analytics_product_metrics_metric_date",
        table_name="plugin_analytics_product_metrics",
    )
    op.drop_index(
        "ix_plugin_analytics_product_metrics_tenant_id",
        table_name="plugin_analytics_product_metrics",
    )
    op.drop_table("plugin_analytics_product_metrics")

    op.drop_index(
        "ix_plugin_analytics_sales_metrics_metric_date",
        table_name="plugin_analytics_sales_metrics",
    )
    op.drop_index(
        "ix_plugin_analytics_sales_metrics_tenant_id",
        table_name="plugin_analytics_sales_metrics",
    )
    op.drop_table("plugin_analytics_sales_metrics")

    op.drop_index(
        "ix_plugin_analytics_report_executions_execution_time",
        table_name="plugin_analytics_report_executions",
    )
    op.drop_index(
        "ix_plugin_analytics_report_executions_report_id",
        table_name="plugin_analytics_report_executions",
    )
    op.drop_index(
        "ix_plugin_analytics_report_executions_tenant_id",
        table_name="plugin_analytics_report_executions",
    )
    op.drop_table("plugin_analytics_report_executions")

    op.drop_index(
        "ix_plugin_analytics_reports_report_type",
        table_name="plugin_analytics_reports",
    )
    op.drop_index(
        "ix_plugin_analytics_reports_tenant_id",
        table_name="plugin_analytics_reports",
    )
    op.drop_table("plugin_analytics_reports")

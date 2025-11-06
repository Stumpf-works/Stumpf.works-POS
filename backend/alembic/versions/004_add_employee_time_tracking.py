"""Add employee time tracking plugin tables

Revision ID: 004_employee_time_tracking
Revises: 003_inventory_management
Create Date: 2025-11-06

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "004_employee_time_tracking"
down_revision: Union[str, None] = "003_inventory_management"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create employee time tracking tables."""
    # Create time_entries table
    op.create_table(
        "plugin_timetracking_entries",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("tenant_id", sa.String(length=100), nullable=False),
        sa.Column("employee_id", sa.Integer(), nullable=False),
        sa.Column("clock_in", sa.DateTime(), nullable=False),
        sa.Column("clock_out", sa.DateTime(), nullable=True),
        sa.Column("total_hours", sa.Numeric(10, 2), nullable=True),
        sa.Column("regular_hours", sa.Numeric(10, 2), nullable=True),
        sa.Column("overtime_hours", sa.Numeric(10, 2), nullable=True),
        sa.Column("break_minutes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("notes", sa.String(length=500), nullable=True),
        sa.Column("approved_by", sa.Integer(), nullable=True),
        sa.Column("approved_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["employee_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["approved_by"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_plugin_timetracking_entries_tenant_id",
        "plugin_timetracking_entries",
        ["tenant_id"],
    )
    op.create_index(
        "ix_plugin_timetracking_entries_employee_id",
        "plugin_timetracking_entries",
        ["employee_id"],
    )
    op.create_index(
        "ix_plugin_timetracking_entries_clock_in",
        "plugin_timetracking_entries",
        ["clock_in"],
    )

    # Create breaks table
    op.create_table(
        "plugin_timetracking_breaks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("tenant_id", sa.String(length=100), nullable=False),
        sa.Column("time_entry_id", sa.Integer(), nullable=False),
        sa.Column("break_start", sa.DateTime(), nullable=False),
        sa.Column("break_end", sa.DateTime(), nullable=True),
        sa.Column("duration_minutes", sa.Integer(), nullable=True),
        sa.Column(
            "break_type", sa.String(length=20), nullable=False, server_default="manual"
        ),
        sa.Column("notes", sa.String(length=500), nullable=True),
        sa.ForeignKeyConstraint(
            ["time_entry_id"],
            ["plugin_timetracking_entries.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_plugin_timetracking_breaks_tenant_id",
        "plugin_timetracking_breaks",
        ["tenant_id"],
    )
    op.create_index(
        "ix_plugin_timetracking_breaks_time_entry_id",
        "plugin_timetracking_breaks",
        ["time_entry_id"],
    )

    # Create shifts table
    op.create_table(
        "plugin_timetracking_shifts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("tenant_id", sa.String(length=100), nullable=False),
        sa.Column("employee_id", sa.Integer(), nullable=False),
        sa.Column("shift_date", sa.DateTime(), nullable=False),
        sa.Column("start_time", sa.DateTime(), nullable=False),
        sa.Column("end_time", sa.DateTime(), nullable=False),
        sa.Column("expected_hours", sa.Numeric(10, 2), nullable=False),
        sa.Column("shift_type", sa.String(length=50), nullable=True),
        sa.Column("notes", sa.String(length=500), nullable=True),
        sa.Column("is_published", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["employee_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["created_by"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_plugin_timetracking_shifts_tenant_id",
        "plugin_timetracking_shifts",
        ["tenant_id"],
    )
    op.create_index(
        "ix_plugin_timetracking_shifts_employee_id",
        "plugin_timetracking_shifts",
        ["employee_id"],
    )
    op.create_index(
        "ix_plugin_timetracking_shifts_shift_date",
        "plugin_timetracking_shifts",
        ["shift_date"],
    )

    # Create overtime table
    op.create_table(
        "plugin_timetracking_overtime",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("tenant_id", sa.String(length=100), nullable=False),
        sa.Column("employee_id", sa.Integer(), nullable=False),
        sa.Column("time_entry_id", sa.Integer(), nullable=True),
        sa.Column("date", sa.DateTime(), nullable=False),
        sa.Column("overtime_hours", sa.Numeric(10, 2), nullable=False),
        sa.Column("reason", sa.String(length=500), nullable=True),
        sa.Column(
            "status", sa.String(length=20), nullable=False, server_default="pending"
        ),
        sa.Column("approved_by", sa.Integer(), nullable=True),
        sa.Column("approved_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["employee_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["time_entry_id"],
            ["plugin_timetracking_entries.id"],
        ),
        sa.ForeignKeyConstraint(
            ["approved_by"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_plugin_timetracking_overtime_tenant_id",
        "plugin_timetracking_overtime",
        ["tenant_id"],
    )
    op.create_index(
        "ix_plugin_timetracking_overtime_employee_id",
        "plugin_timetracking_overtime",
        ["employee_id"],
    )
    op.create_index(
        "ix_plugin_timetracking_overtime_date",
        "plugin_timetracking_overtime",
        ["date"],
    )


def downgrade() -> None:
    """Drop employee time tracking tables."""
    op.drop_index(
        "ix_plugin_timetracking_overtime_date",
        table_name="plugin_timetracking_overtime",
    )
    op.drop_index(
        "ix_plugin_timetracking_overtime_employee_id",
        table_name="plugin_timetracking_overtime",
    )
    op.drop_index(
        "ix_plugin_timetracking_overtime_tenant_id",
        table_name="plugin_timetracking_overtime",
    )
    op.drop_table("plugin_timetracking_overtime")

    op.drop_index(
        "ix_plugin_timetracking_shifts_shift_date",
        table_name="plugin_timetracking_shifts",
    )
    op.drop_index(
        "ix_plugin_timetracking_shifts_employee_id",
        table_name="plugin_timetracking_shifts",
    )
    op.drop_index(
        "ix_plugin_timetracking_shifts_tenant_id",
        table_name="plugin_timetracking_shifts",
    )
    op.drop_table("plugin_timetracking_shifts")

    op.drop_index(
        "ix_plugin_timetracking_breaks_time_entry_id",
        table_name="plugin_timetracking_breaks",
    )
    op.drop_index(
        "ix_plugin_timetracking_breaks_tenant_id",
        table_name="plugin_timetracking_breaks",
    )
    op.drop_table("plugin_timetracking_breaks")

    op.drop_index(
        "ix_plugin_timetracking_entries_clock_in",
        table_name="plugin_timetracking_entries",
    )
    op.drop_index(
        "ix_plugin_timetracking_entries_employee_id",
        table_name="plugin_timetracking_entries",
    )
    op.drop_index(
        "ix_plugin_timetracking_entries_tenant_id",
        table_name="plugin_timetracking_entries",
    )
    op.drop_table("plugin_timetracking_entries")

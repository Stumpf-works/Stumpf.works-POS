"""Add plugin_licenses table

Revision ID: 001_plugin_licenses
Revises:
Create Date: 2025-11-06

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_plugin_licenses'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create plugin_licenses table."""
    op.create_table(
        'plugin_licenses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),

        # Core fields
        sa.Column('tenant_id', sa.String(length=100), nullable=False),
        sa.Column('plugin_name', sa.String(length=100), nullable=False),

        # License status
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),

        # License validity
        sa.Column('valid_from', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('valid_until', sa.DateTime(), nullable=True),

        # License metadata
        sa.Column('license_type', sa.String(length=50), nullable=False, server_default='standard'),
        sa.Column('max_users', sa.Integer(), nullable=True),
        sa.Column('max_locations', sa.Integer(), nullable=True),

        # Additional config
        sa.Column('config', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),

        # Audit trail
        sa.Column('granted_by', sa.Integer(), nullable=True),
        sa.Column('granted_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),

        # Primary key
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes
    op.create_index(
        'ix_plugin_licenses_tenant_id',
        'plugin_licenses',
        ['tenant_id']
    )

    op.create_index(
        'ix_plugin_licenses_plugin_name',
        'plugin_licenses',
        ['plugin_name']
    )

    # Create unique constraint (one license per plugin per tenant)
    op.create_index(
        'uq_plugin_licenses_tenant_plugin',
        'plugin_licenses',
        ['tenant_id', 'plugin_name'],
        unique=True
    )


def downgrade() -> None:
    """Drop plugin_licenses table."""
    op.drop_index('uq_plugin_licenses_tenant_plugin', table_name='plugin_licenses')
    op.drop_index('ix_plugin_licenses_plugin_name', table_name='plugin_licenses')
    op.drop_index('ix_plugin_licenses_tenant_id', table_name='plugin_licenses')
    op.drop_table('plugin_licenses')

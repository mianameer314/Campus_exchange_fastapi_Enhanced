"""add admin review fields to verification

Revision ID: d7f3a8b9c2e1
Revises: c9d8e5f2a1b4
Create Date: 2025-08-18 17:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'd7f3a8b9c2e1'
down_revision = 'c9d8e5f2a1b4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add reviewed_at column
    op.add_column('verifications', sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True))
    
    # Add admin_notes column
    op.add_column('verifications', sa.Column('admin_notes', sa.Text(), nullable=True))


def downgrade() -> None:
    # Remove admin_notes column
    op.drop_column('verifications', 'admin_notes')
    
    # Remove reviewed_at column
    op.drop_column('verifications', 'reviewed_at')

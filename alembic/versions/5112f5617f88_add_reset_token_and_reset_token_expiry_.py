"""Add reset_token and reset_token_expiry to users table

Revision ID: 5112f5617f88
Revises: 20250822_add_reviews_table
Create Date: 2025-08-25 18:28:12.327953

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5112f5617f88'
down_revision: Union[str, Sequence[str], None] = '20250822_add_reviews_table'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add reset_token and reset_token_expiry
    op.add_column('users', sa.Column('reset_token', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('reset_token_expiry', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    # Drop reset_token and reset_token_expiry
    op.drop_column('users', 'reset_token_expiry')
    op.drop_column('users', 'reset_token')
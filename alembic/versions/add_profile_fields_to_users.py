"""Add profile fields to users (full_name, university_name, phone) and drop old university

Revision ID: add_profile_fields_to_users
Revises: f5e8a9b3c7d2
Create Date: 2025-08-22 15:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "add_profile_fields_to_users"
down_revision: Union[str, Sequence[str], None] = "f5e8a9b3c7d2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new profile fields
    op.add_column("users", sa.Column("full_name", sa.String(length=255), nullable=True))
    op.add_column("users", sa.Column("university_name", sa.String(length=255), nullable=True))
    op.add_column("users", sa.Column("phone", sa.String(length=20), nullable=True))

    # Drop old university column if it exists
    with op.batch_alter_table("users") as batch_op:
        try:
            batch_op.drop_column("university")
        except Exception:
            # column might already be gone
            pass


def downgrade() -> None:
    # Recreate old column
    op.add_column("users", sa.Column("university", sa.String(length=255), nullable=True))

    # Drop new profile fields
    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_column("phone")
        batch_op.drop_column("university_name")
        batch_op.drop_column("full_name")

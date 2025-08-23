"""Add reviews table for user ratings

Revision ID: 20250822_add_reviews_table
Revises: 20250822_enhance_user_profile
Create Date: 2025-08-22 20:00:00
"""
from alembic import op
import sqlalchemy as sa

revision = "20250822_add_reviews_table"
down_revision = "20250822_enhance_user_profile"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "reviews",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("reviewer_id", sa.String(length=100), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("reviewed_id", sa.String(length=100), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("rating", sa.Integer, nullable=False),
        sa.Column("comment", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
    )

    # optional: ensure a user can only review another user once
    op.create_unique_constraint(
        "uq_reviewer_reviewed", "reviews", ["reviewer_id", "reviewed_id"]
    )


def downgrade() -> None:
    op.drop_constraint("uq_reviewer_reviewed", "reviews", type_="unique")
    op.drop_table("reviews")

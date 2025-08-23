"""Enhance user profile with marketplace fields

Revision ID: 20250822_enhance_user_profile
Revises: add_profile_fields_to_users
Create Date: 2025-08-22 18:30:00
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# IMPORTANT: If your current head isn't 'add_profile_fields', replace with your actual head.
revision = "20250822_enhance_user_profile"
down_revision = "add_profile_fields_to_users"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("users") as batch_op:
        # identity
        batch_op.add_column(sa.Column("profile_picture", sa.String(length=512), nullable=True))
        batch_op.add_column(sa.Column("bio", sa.Text(), nullable=True))

        # campus
        batch_op.add_column(sa.Column("student_id", sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column("department", sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column("year_of_study", sa.Integer(), nullable=True))

        # contact
        batch_op.add_column(sa.Column("whatsapp_number", sa.String(length=50), nullable=True))

        # reputation
        batch_op.add_column(sa.Column("rating", sa.Float(), nullable=False, server_default="0"))
        batch_op.add_column(sa.Column("reviews_count", sa.Integer(), nullable=False, server_default="0"))
        batch_op.add_column(sa.Column("verified_badge", sa.Boolean(), nullable=False, server_default=sa.text("false")))

        # preferences
        batch_op.add_column(sa.Column("notification_preferences", postgresql.JSON(astext_type=sa.Text()), nullable=True))
        batch_op.add_column(sa.Column("preferred_categories", postgresql.ARRAY(sa.String(length=100)), nullable=True))

        # audit
        batch_op.add_column(sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False))
        batch_op.add_column(sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False))

    # ✅ Drop defaults inside the same transaction
    op.execute("ALTER TABLE users ALTER COLUMN rating DROP DEFAULT;")
    op.execute("ALTER TABLE users ALTER COLUMN reviews_count DROP DEFAULT;")
    op.execute("ALTER TABLE users ALTER COLUMN verified_badge DROP DEFAULT;")
    op.execute("ALTER TABLE users ALTER COLUMN created_at DROP DEFAULT;")
    op.execute("ALTER TABLE users ALTER COLUMN updated_at DROP DEFAULT;")


def downgrade() -> None:
    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_column("updated_at")
        batch_op.drop_column("created_at")
        batch_op.drop_column("last_login_at")
        batch_op.drop_column("preferred_categories")
        batch_op.drop_column("notification_preferences")
        batch_op.drop_column("verified_badge")
        batch_op.drop_column("reviews_count")
        batch_op.drop_column("rating")
        batch_op.drop_column("whatsapp_number")
        batch_op.drop_column("year_of_study")
        batch_op.drop_column("department")
        batch_op.drop_column("student_id")
        batch_op.drop_column("bio")
        batch_op.drop_column("profile_picture")
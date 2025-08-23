"""Update listing owner_id to string

Revision ID: f5e8a9b3c7d2
Revises: 681c3f862be8
Create Date: 2024-01-20 10:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f5e8a9b3c7d2'
down_revision = '681c3f862be8'  # Updated to point to the latest migration
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint('listings_owner_id_fkey', 'listings', type_='foreignkey')
    
    op.alter_column('listings', 'owner_id',
                   existing_type=sa.INTEGER(),
                   type_=sa.String(length=100),
                   existing_nullable=False)
    
    op.create_foreign_key('listings_owner_id_fkey', 'listings', 'users', 
                         ['owner_id'], ['id'])


def downgrade() -> None:
    op.drop_constraint('listings_owner_id_fkey', 'listings', type_='foreignkey')
    
    op.alter_column('listings', 'owner_id',
                   existing_type=sa.String(length=100),
                   type_=sa.INTEGER(),
                   existing_nullable=False)
    
    op.create_foreign_key('listings_owner_id_fkey', 'listings', 'users', 
                         ['owner_id'], ['id'])

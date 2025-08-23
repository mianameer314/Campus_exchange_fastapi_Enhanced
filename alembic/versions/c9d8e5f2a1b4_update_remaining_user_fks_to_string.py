"""Update remaining user foreign keys to string

Revision ID: c9d8e5f2a1b4
Revises: b8f4c2a1d9e3
Create Date: 2024-01-15 10:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c9d8e5f2a1b4'
down_revision = 'b8f4c2a1d9e3'
branch_labels = None
depends_on = None


def upgrade():
    
    # Drop foreign key constraints for ChatMessage
    op.drop_constraint('chat_messages_sender_id_fkey', 'chat_messages', type_='foreignkey')
    op.drop_constraint('chat_messages_receiver_id_fkey', 'chat_messages', type_='foreignkey')
    
    # Alter columns to String(100)
    op.alter_column('chat_messages', 'sender_id',
                    existing_type=sa.Integer(),
                    type_=sa.String(100),
                    existing_nullable=False)
    op.alter_column('chat_messages', 'receiver_id',
                    existing_type=sa.Integer(),
                    type_=sa.String(100),
                    existing_nullable=False)
    
    # Recreate foreign key constraints
    op.create_foreign_key('chat_messages_sender_id_fkey', 'chat_messages', 'users', ['sender_id'], ['id'])
    op.create_foreign_key('chat_messages_receiver_id_fkey', 'chat_messages', 'users', ['receiver_id'], ['id'])
    
    
    # Drop foreign key constraints for Report
    op.drop_constraint('reports_reporter_id_fkey', 'reports', type_='foreignkey')
    op.drop_constraint('reports_reported_user_id_fkey', 'reports', type_='foreignkey')
    op.drop_constraint('reports_reviewed_by_fkey', 'reports', type_='foreignkey')
    
    # Alter columns to String(100)
    op.alter_column('reports', 'reporter_id',
                    existing_type=sa.Integer(),
                    type_=sa.String(100),
                    existing_nullable=False)
    op.alter_column('reports', 'reported_user_id',
                    existing_type=sa.Integer(),
                    type_=sa.String(100),
                    existing_nullable=True)
    op.alter_column('reports', 'reviewed_by',
                    existing_type=sa.Integer(),
                    type_=sa.String(100),
                    existing_nullable=True)
    
    # Recreate foreign key constraints
    op.create_foreign_key('reports_reporter_id_fkey', 'reports', 'users', ['reporter_id'], ['id'])
    op.create_foreign_key('reports_reported_user_id_fkey', 'reports', 'users', ['reported_user_id'], ['id'])
    op.create_foreign_key('reports_reviewed_by_fkey', 'reports', 'users', ['reviewed_by'], ['id'])


def downgrade():
    
    # Drop foreign key constraints for Report
    op.drop_constraint('reports_reviewed_by_fkey', 'reports', type_='foreignkey')
    op.drop_constraint('reports_reported_user_id_fkey', 'reports', type_='foreignkey')
    op.drop_constraint('reports_reporter_id_fkey', 'reports', type_='foreignkey')
    
    # Alter columns back to Integer
    op.alter_column('reports', 'reviewed_by',
                    existing_type=sa.String(100),
                    type_=sa.Integer(),
                    existing_nullable=True)
    op.alter_column('reports', 'reported_user_id',
                    existing_type=sa.String(100),
                    type_=sa.Integer(),
                    existing_nullable=True)
    op.alter_column('reports', 'reporter_id',
                    existing_type=sa.String(100),
                    type_=sa.Integer(),
                    existing_nullable=False)
    
    # Recreate foreign key constraints
    op.create_foreign_key('reports_reviewed_by_fkey', 'reports', 'users', ['reviewed_by'], ['id'])
    op.create_foreign_key('reports_reported_user_id_fkey', 'reports', 'users', ['reported_user_id'], ['id'])
    op.create_foreign_key('reports_reporter_id_fkey', 'reports', 'users', ['reporter_id'], ['id'])
    
    
    # Drop foreign key constraints for ChatMessage
    op.drop_constraint('chat_messages_receiver_id_fkey', 'chat_messages', type_='foreignkey')
    op.drop_constraint('chat_messages_sender_id_fkey', 'chat_messages', type_='foreignkey')
    
    # Alter columns back to Integer
    op.alter_column('chat_messages', 'receiver_id',
                    existing_type=sa.String(100),
                    type_=sa.Integer(),
                    existing_nullable=False)
    op.alter_column('chat_messages', 'sender_id',
                    existing_type=sa.String(100),
                    type_=sa.Integer(),
                    existing_nullable=False)
    
    # Recreate foreign key constraints
    op.create_foreign_key('chat_messages_receiver_id_fkey', 'chat_messages', 'users', ['receiver_id'], ['id'])
    op.create_foreign_key('chat_messages_sender_id_fkey', 'chat_messages', 'users', ['sender_id'], ['id'])

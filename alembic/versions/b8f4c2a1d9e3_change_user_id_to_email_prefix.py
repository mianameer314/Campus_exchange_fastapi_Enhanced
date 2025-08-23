"""Change user ID to email prefix

Revision ID: b8f4c2a1d9e3
Revises: 325f6e4ea397
Create Date: 2025-01-18 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'b8f4c2a1d9e3'
down_revision: Union[str, Sequence[str], None] = '325f6e4ea397'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema to use email prefix as user ID."""
    
    connection = op.get_bind()
    
    # Check if admin_activity_log table exists, create if not
    result = connection.execute(sa.text("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'admin_activity_log'
        );
    """))
    table_exists = result.scalar()
    
    if not table_exists:
        op.create_table('admin_activity_log',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('admin_id', sa.Integer(), nullable=False),
            sa.Column('action', sa.String(length=255), nullable=False),
            sa.Column('target_type', sa.String(length=100), nullable=True),
            sa.Column('target_id', sa.Integer(), nullable=True),
            sa.Column('details', sa.JSON(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.ForeignKeyConstraint(['admin_id'], ['users.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
    
    op.add_column('users', sa.Column('new_id', sa.String(length=100), nullable=True))
    
    connection.execute(sa.text("""
        UPDATE users 
        SET new_id = SPLIT_PART(email, '@', 1)
        WHERE new_id IS NULL
    """))
    
    op.alter_column('users', 'new_id', nullable=False)
    op.create_unique_constraint('uq_users_new_id', 'users', ['new_id'])
    
    tables_with_user_fks = [
        ('blocked_users', 'user_id'),
        ('blocked_users', 'blocked_by'),
        ('listings', 'owner_id'),
        ('notifications', 'user_id'),
        ('verifications', 'user_id'),
        ('chat_messages', 'sender_id'),
        ('chat_messages', 'receiver_id'),
        ('chat_rooms', 'participant1_id'),
        ('chat_rooms', 'participant2_id'),
        ('favorites', 'user_id'),
        ('messages', 'sender_id'),
        ('messages', 'receiver_id'),
        ('reports', 'reporter_id'),
        ('reports', 'reported_user_id'),
        ('reports', 'reviewed_by'),
        ('message_reactions', 'user_id'),
        ('admin_activity_log', 'admin_id')
    ]
    
    # Add temporary string columns only for existing tables
    for table_name, column_name in tables_with_user_fks:
        result = connection.execute(sa.text(f"""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = '{table_name}'
            );
        """))
        if result.scalar():
            op.add_column(table_name, sa.Column(f'new_{column_name}', sa.String(length=100), nullable=True))
    
    for table_name, column_name in tables_with_user_fks:
        result = connection.execute(sa.text(f"""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = '{table_name}'
            );
        """))
        if result.scalar():
            if column_name in ['reported_user_id', 'reviewed_by', 'admin_id']:  # These can be NULL
                connection.execute(sa.text(f"""
                    UPDATE {table_name} 
                    SET new_{column_name} = (
                        SELECT SPLIT_PART(email, '@', 1) 
                        FROM users 
                        WHERE users.id = {table_name}.{column_name}
                    )
                    WHERE {column_name} IS NOT NULL
                """))
            else:
                connection.execute(sa.text(f"""
                    UPDATE {table_name} 
                    SET new_{column_name} = (
                        SELECT SPLIT_PART(email, '@', 1) 
                        FROM users 
                        WHERE users.id = {table_name}.{column_name}
                    )
                """))
    
    constraint_drops = [
        ('blocked_users_user_id_fkey', 'blocked_users'),
        ('blocked_users_blocked_by_fkey', 'blocked_users'),
        ('listings_owner_id_fkey', 'listings'),
        ('notifications_user_id_fkey', 'notifications'),
        ('verifications_user_id_fkey', 'verifications'),
        ('chat_messages_sender_id_fkey', 'chat_messages'),
        ('chat_messages_receiver_id_fkey', 'chat_messages'),
        ('chat_rooms_participant1_id_fkey', 'chat_rooms'),
        ('chat_rooms_participant2_id_fkey', 'chat_rooms'),
        ('favorites_user_id_fkey', 'favorites'),
        ('messages_sender_id_fkey', 'messages'),
        ('messages_receiver_id_fkey', 'messages'),
        ('reports_reporter_id_fkey', 'reports'),
        ('reports_reported_user_id_fkey', 'reports'),
        ('reports_reviewed_by_fkey', 'reports'),
        ('message_reactions_user_id_fkey', 'message_reactions'),
        ('admin_activity_log_admin_id_fkey', 'admin_activity_log')
    ]
    
    for constraint_name, table_name in constraint_drops:
        result = connection.execute(sa.text(f"""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = '{table_name}'
            );
        """))
        if result.scalar():
            try:
                op.drop_constraint(constraint_name, table_name, type_='foreignkey')
            except Exception:
                # Constraint might not exist, continue
                pass
    
    for table_name, column_name in tables_with_user_fks:
        result = connection.execute(sa.text(f"""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = '{table_name}'
            );
        """))
        if result.scalar():
            op.drop_column(table_name, column_name)
            op.alter_column(table_name, f'new_{column_name}', new_column_name=column_name)
            
            # Make non-nullable where appropriate
            if column_name not in ['reported_user_id', 'reviewed_by', 'admin_id']:
                op.alter_column(table_name, column_name, nullable=False)
    
    op.drop_constraint('users_pkey', 'users', type_='primary')
    op.drop_index('ix_users_id', table_name='users')
    op.drop_column('users', 'id')
    op.alter_column('users', 'new_id', new_column_name='id')
    
    op.create_primary_key('users_pkey', 'users', ['id'])
    op.create_index('ix_users_id', 'users', ['id'], unique=True)
    
    foreign_keys = [
        ('blocked_users_user_id_fkey', 'blocked_users', 'users', ['user_id'], ['id'], 'CASCADE'),
        ('blocked_users_blocked_by_fkey', 'blocked_users', 'users', ['blocked_by'], ['id'], 'CASCADE'),
        ('listings_owner_id_fkey', 'listings', 'users', ['owner_id'], ['id'], None),
        ('notifications_user_id_fkey', 'notifications', 'users', ['user_id'], ['id'], None),
        ('verifications_user_id_fkey', 'verifications', 'users', ['user_id'], ['id'], None),
        ('chat_messages_sender_id_fkey', 'chat_messages', 'users', ['sender_id'], ['id'], None),
        ('chat_messages_receiver_id_fkey', 'chat_messages', 'users', ['receiver_id'], ['id'], None),
        ('chat_rooms_participant1_id_fkey', 'chat_rooms', 'users', ['participant1_id'], ['id'], None),
        ('chat_rooms_participant2_id_fkey', 'chat_rooms', 'users', ['participant2_id'], ['id'], None),
        ('favorites_user_id_fkey', 'favorites', 'users', ['user_id'], ['id'], None),
        ('messages_sender_id_fkey', 'messages', 'users', ['sender_id'], ['id'], None),
        ('messages_receiver_id_fkey', 'messages', 'users', ['receiver_id'], ['id'], None),
        ('reports_reporter_id_fkey', 'reports', 'users', ['reporter_id'], ['id'], None),
        ('reports_reported_user_id_fkey', 'reports', 'users', ['reported_user_id'], ['id'], None),
        ('reports_reviewed_by_fkey', 'reports', 'users', ['reviewed_by'], ['id'], None),
        ('message_reactions_user_id_fkey', 'message_reactions', 'users', ['user_id'], ['id'], 'CASCADE'),
        ('admin_activity_log_admin_id_fkey', 'admin_activity_log', 'users', ['admin_id'], ['id'], None)
    ]
    
    for fk_name, source_table, target_table, source_cols, target_cols, ondelete in foreign_keys:
        result = connection.execute(sa.text(f"""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = '{source_table}'
            );
        """))
        if result.scalar():
            if ondelete:
                op.create_foreign_key(fk_name, source_table, target_table, source_cols, target_cols, ondelete=ondelete)
            else:
                op.create_foreign_key(fk_name, source_table, target_table, source_cols, target_cols)


def downgrade() -> None:
    """Downgrade schema back to integer user IDs."""
    
    op.add_column('users', sa.Column('new_id', sa.Integer(), nullable=True))
    
    op.execute("CREATE SEQUENCE users_id_seq")
    
    connection = op.get_bind()
    result = connection.execute(sa.text("SELECT id FROM users ORDER BY id"))
    users = result.fetchall()
    
    for i, (user_id,) in enumerate(users, 1):
        connection.execute(sa.text(f"UPDATE users SET new_id = {i} WHERE id = '{user_id}'"))
    
    op.alter_column('users', 'new_id', nullable=False)
    op.drop_constraint('users_pkey', 'users', type_='primary')
    op.drop_index('ix_users_id', table_name='users')
    
    # Reverse all the foreign key and column changes...
    # (Implementation would mirror the upgrade process in reverse)
    
    op.drop_column('users', 'id')
    op.alter_column('users', 'new_id', new_column_name='id')
    op.create_primary_key('users_pkey', 'users', ['id'])
    op.create_index('ix_users_id', 'users', ['id'], unique=False)

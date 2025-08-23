"""Update chat and reaction user IDs to String(100)

Revision ID: 681c3f862be8
Revises: d7f3a8b9c2e1
Create Date: 2025-08-18 21:43:02.186921

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '681c3f862be8'
down_revision: Union[str, Sequence[str], None] = 'd7f3a8b9c2e1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- Chat Messages ---
    op.drop_constraint('chat_messages_sender_id_fkey', 'chat_messages', type_='foreignkey')
    op.drop_constraint('chat_messages_receiver_id_fkey', 'chat_messages', type_='foreignkey')

    op.alter_column('chat_messages', 'sender_id',
                    existing_type=sa.Integer(),
                    type_=sa.String(100),
                    existing_nullable=False)
    op.alter_column('chat_messages', 'receiver_id',
                    existing_type=sa.Integer(),
                    type_=sa.String(100),
                    existing_nullable=False)

    op.create_foreign_key('chat_messages_sender_id_fkey', 'chat_messages', 'users', ['sender_id'], ['id'])
    op.create_foreign_key('chat_messages_receiver_id_fkey', 'chat_messages', 'users', ['receiver_id'], ['id'])

    # --- Chat Rooms ---
    op.drop_constraint('chat_rooms_participant1_id_fkey', 'chat_rooms', type_='foreignkey')
    op.drop_constraint('chat_rooms_participant2_id_fkey', 'chat_rooms', type_='foreignkey')

    op.alter_column('chat_rooms', 'participant1_id',
                    existing_type=sa.Integer(),
                    type_=sa.String(100),
                    existing_nullable=False)
    op.alter_column('chat_rooms', 'participant2_id',
                    existing_type=sa.Integer(),
                    type_=sa.String(100),
                    existing_nullable=False)

    op.create_foreign_key('chat_rooms_participant1_id_fkey', 'chat_rooms', 'users', ['participant1_id'], ['id'])
    op.create_foreign_key('chat_rooms_participant2_id_fkey', 'chat_rooms', 'users', ['participant2_id'], ['id'])

    # --- Message Reactions ---
    op.drop_constraint('message_reactions_user_id_fkey', 'message_reactions', type_='foreignkey')

    op.alter_column('message_reactions', 'user_id',
                    existing_type=sa.Integer(),
                    type_=sa.String(100),
                    existing_nullable=False)

    op.create_foreign_key('message_reactions_user_id_fkey', 'message_reactions', 'users', ['user_id'], ['id'], ondelete="CASCADE")


def downgrade() -> None:
    # --- Message Reactions ---
    op.drop_constraint('message_reactions_user_id_fkey', 'message_reactions', type_='foreignkey')
    op.alter_column('message_reactions', 'user_id',
                    existing_type=sa.String(100),
                    type_=sa.Integer(),
                    existing_nullable=False)
    op.create_foreign_key('message_reactions_user_id_fkey', 'message_reactions', 'users', ['user_id'], ['id'], ondelete="CASCADE")

    # --- Chat Rooms ---
    op.drop_constraint('chat_rooms_participant1_id_fkey', 'chat_rooms', type_='foreignkey')
    op.drop_constraint('chat_rooms_participant2_id_fkey', 'chat_rooms', type_='foreignkey')

    op.alter_column('chat_rooms', 'participant1_id',
                    existing_type=sa.String(100),
                    type_=sa.Integer(),
                    existing_nullable=False)
    op.alter_column('chat_rooms', 'participant2_id',
                    existing_type=sa.String(100),
                    type_=sa.Integer(),
                    existing_nullable=False)

    op.create_foreign_key('chat_rooms_participant1_id_fkey', 'chat_rooms', 'users', ['participant1_id'], ['id'])
    op.create_foreign_key('chat_rooms_participant2_id_fkey', 'chat_rooms', 'users', ['participant2_id'], ['id'])

    # --- Chat Messages ---
    op.drop_constraint('chat_messages_sender_id_fkey', 'chat_messages', type_='foreignkey')
    op.drop_constraint('chat_messages_receiver_id_fkey', 'chat_messages', type_='foreignkey')

    op.alter_column('chat_messages', 'sender_id',
                    existing_type=sa.String(100),
                    type_=sa.Integer(),
                    existing_nullable=False)
    op.alter_column('chat_messages', 'receiver_id',
                    existing_type=sa.String(100),
                    type_=sa.Integer(),
                    existing_nullable=False)

    op.create_foreign_key('chat_messages_sender_id_fkey', 'chat_messages', 'users', ['sender_id'], ['id'])
    op.create_foreign_key('chat_messages_receiver_id_fkey', 'chat_messages', 'users', ['receiver_id'], ['id'])

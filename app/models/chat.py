from sqlalchemy import Column, Integer, ForeignKey, Text, DateTime, Boolean, UniqueConstraint, String, JSON
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from app.db.session import Base
from typing import Optional, List
from datetime import datetime

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    listing_id: Mapped[int] = mapped_column(Integer, ForeignKey('listings.id'), nullable=False)
    sender_id: Mapped[str] = mapped_column(String(100), ForeignKey('users.id'), nullable=False)
    receiver_id: Mapped[str] = mapped_column(String(100), ForeignKey("users.id"), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    edited: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    message_type: Mapped[str] = mapped_column(String(20), default="text", nullable=False)  # text, image, file, system
    message_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # For file info, image dimensions, etc.
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    reply_to_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('chat_messages.id'), nullable=True)

    listing = relationship("Listing", back_populates="messages")
    sender = relationship("User", foreign_keys=[sender_id])
    receiver = relationship("User", foreign_keys=[receiver_id])
    reply_to = relationship("ChatMessage", remote_side=[id], backref="replies")

class ChatRoom(Base):
    __tablename__ = "chat_rooms"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    listing_id: Mapped[int] = mapped_column(Integer, ForeignKey('listings.id'), nullable=False)
    participant1_id: Mapped[str] = mapped_column(String(100), ForeignKey('users.id'), nullable=False)
    participant2_id: Mapped[str] = mapped_column(String(100), ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_message_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)  # active, archived, blocked
    settings: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Room-specific settings
    
    listing = relationship("Listing")
    participant1 = relationship("User", foreign_keys=[participant1_id])
    participant2 = relationship("User", foreign_keys=[participant2_id])
    
    __table_args__ = (UniqueConstraint('listing_id', 'participant1_id', 'participant2_id', name='uq_chat_room'),)

class BlockedUser(Base):
    __tablename__ = "blocked_users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[str] = mapped_column(String(100), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    blocked_by: Mapped[str] = mapped_column(String(100), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    blocker = relationship("User", foreign_keys=[blocked_by])

    __table_args__ = (UniqueConstraint('user_id', 'blocked_by', name='uq_user_blocked_by'),)

class MessageReaction(Base):
    __tablename__ = "message_reactions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    message_id: Mapped[int] = mapped_column(Integer, ForeignKey('chat_messages.id', ondelete="CASCADE"), nullable=False)
    user_id: Mapped[str] = mapped_column(String(100), ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    reaction: Mapped[str] = mapped_column(String(10), nullable=False)  # emoji or reaction type
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    message = relationship("ChatMessage", backref="reactions")
    user = relationship("User")
    
    __table_args__ = (UniqueConstraint('message_id', 'user_id', 'reaction', name='uq_message_user_reaction'),)
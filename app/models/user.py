from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, DateTime, Float, Integer, Text, func
from sqlalchemy.dialects.postgresql import JSON, ARRAY
from app.db.session import Base


class User(Base):
    __tablename__ = "users"

    # PK and auth
    id: Mapped[str] = mapped_column(String(100), primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    # identity
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    profile_picture: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # campus
    university_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    student_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    department: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    year_of_study: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # contact
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    whatsapp_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # flags
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    verified_badge: Mapped[bool] = mapped_column(Boolean, default=False)

    # reputation
    rating: Mapped[float] = mapped_column(Float, default=0.0)
    reviews_count: Mapped[int] = mapped_column(Integer, default=0)

    # preferences
    notification_preferences: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)
    preferred_categories: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String(100)), default=list)

    # audit
    last_login_at: Mapped[Optional["datetime"]] = mapped_column(DateTime(timezone=True), nullable=True) # type: ignore
    created_at: Mapped["datetime"] = mapped_column(DateTime(timezone=True), default=func.now())
    updated_at: Mapped["datetime"] = mapped_column(DateTime(timezone=True), default=func.now(), onupdate=func.now())

    # relationships
    listings: Mapped[List["Listing"]] = relationship("Listing", back_populates="owner")
    favorites: Mapped[List["Favorite"]] = relationship("Favorite", back_populates="user")
    notifications: Mapped[List["Notification"]] = relationship("Notification", back_populates="user")
    verifications = relationship("Verification", back_populates="user")

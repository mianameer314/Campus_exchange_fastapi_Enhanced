from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import JSON, String, Integer, ForeignKey, Numeric, Text, DateTime, func
from datetime import datetime
from typing import List as SAList, Optional
from app.db.session import Base
from sqlalchemy.orm import deferred
from sqlalchemy.dialects.postgresql import TSVECTOR 


class Listing(Base):
    __tablename__ = "listings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[str] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(100), index=True)
    price: Mapped[float] = mapped_column(Numeric(10, 2))
    images: Mapped[Optional[list[str]]] = mapped_column(JSON, nullable=True)  # store as list of URLs
    search_vector: Mapped[Optional[str]] = deferred(mapped_column(TSVECTOR, nullable=True))

    status: Mapped[str] = mapped_column(String(20), index=True, default="ACTIVE")  # ACTIVE | SOLD | ARCHIVED
    owner_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    owner: Mapped["User"] = relationship("User", back_populates="listings")
    favorites: Mapped[SAList["Favorite"]] = relationship("Favorite", back_populates="listing")

    messages = relationship("ChatMessage", back_populates="listing")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "price": float(self.price),
            "images": self.images or [],
            "status": self.status,
            "owner_id": self.owner_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

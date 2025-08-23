from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.sql import func
from app.db.session import Base
from enum import Enum as PyEnum
from sqlalchemy import Enum as SQLEnum

class ReportStatus(str, PyEnum):
    PENDING = "PENDING"
    REVIEWED = "REVIEWED"
    REJECTED = "REJECTED"
    RESOLVED = "RESOLVED"

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    reporter_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reported_listing_id = Column(Integer, ForeignKey("listings.id"), nullable=True)
    reported_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    reason = Column(Text, nullable=False)
    status = Column(SQLEnum(ReportStatus), default=ReportStatus.PENDING, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    audit_log = Column(Text, nullable=True)

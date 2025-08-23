from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime

class ReportCreate(BaseModel):
    reported_listing_id: Optional[int] = None
    reported_user_id: Optional[str] = None
    reason: str

    @field_validator('reported_listing_id')
    @classmethod
    def listing_id_must_be_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError('reported_listing_id must be a positive integer or null')
        return v

    @field_validator('reported_user_id')
    @classmethod
    def user_id_must_be_valid(cls, v):
        if v is not None and (not v or v.strip() == ""):
            raise ValueError('reported_user_id must be a valid string or null')
        return v

    @field_validator('reason')
    @classmethod
    def reason_not_empty(cls, v):
        if not v or v.strip() == "":
            raise ValueError('reason is required and cannot be empty')
        return v

class ReportOut(BaseModel):
    id: int
    reporter_id: str
    reported_listing_id: Optional[int]
    reported_user_id: Optional[str]
    reason: str
    status: str
    created_at: datetime
    reviewed_by: Optional[str]
    reviewed_at: Optional[datetime]
    audit_log: Optional[str]

    class Config:
        from_attributes = True

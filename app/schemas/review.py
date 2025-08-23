# app/schemas/review.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ReviewIn(BaseModel):
    reviewed_id: str
    rating: int
    comment: Optional[str] = None

class ReviewOut(BaseModel):
    id: int
    reviewer_id: str
    reviewed_id: str
    rating: int
    comment: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

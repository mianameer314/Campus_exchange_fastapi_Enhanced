from typing import List, Optional, Dict
from pydantic import BaseModel, EmailStr
from datetime import datetime


class ProfileOut(BaseModel):
    # core
    id: str
    email: EmailStr
    is_admin: bool
    is_verified: bool

    # identity
    full_name: Optional[str] = None
    bio: Optional[str] = None

    # campus
    university_name: Optional[str] = None
    student_id: Optional[str] = None
    department: Optional[str] = None
    year_of_study: Optional[int] = None

    # contact
    phone: Optional[str] = None
    whatsapp_number: Optional[str] = None

    # reputation
    rating: float = 0.0
    reviews_count: int = 0
    verified_badge: bool = False

    # preferences
    notification_preferences: Optional[Dict] = None
    preferred_categories: Optional[List[str]] = None

    # audit
    last_login_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ProfileUpdate(BaseModel):
    # all fields optional so PATCH is truly partial
    full_name: Optional[str] = None
    profile_picture: Optional[str] = None
    bio: Optional[str] = None

    university_name: Optional[str] = None
    student_id: Optional[str] = None
    department: Optional[str] = None
    year_of_study: Optional[int] = None

    phone: Optional[str] = None
    whatsapp_number: Optional[str] = None

    notification_preferences: Optional[dict] = None
    preferred_categories: Optional[List[str]] = None


class DeleteAccountIn(BaseModel):
    password: str

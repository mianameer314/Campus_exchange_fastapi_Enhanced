from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Generic, TypeVar
from datetime import datetime

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int

class AdminUserOut(BaseModel):
    id: str  # Changed from int to str for string user IDs
    email: str
    is_admin: bool
    is_verified: bool
    is_active: bool
    university: Optional[str]
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class AdminListingOut(BaseModel):
    id: int
    title: str
    description: str
    category: str
    price: float
    status: str
    owner_id: str  # Changed from int to str for string user IDs
    created_at: datetime
    updated_at: datetime
    owner: Optional[AdminUserOut] = None
    
    class Config:
        from_attributes = True

class AdminReportOut(BaseModel):
    id: int
    report_type: str
    reason: str
    status: str
    created_at: datetime
    resolved_at: Optional[datetime] = None
    reporter_id: str  # Changed from int to str for string user IDs
    reported_user_id: Optional[str] = None
    listing_id: Optional[int] = None
    admin_notes: Optional[str] = None
    
    class Config:
        from_attributes = True

class AdminVerificationOut(BaseModel):
    id: int
    user_id: str
    status: str
    created_at: datetime
    reviewed_at: Optional[datetime] = None
    admin_notes: Optional[str] = None
    
    class Config:
        from_attributes = True

class PaginatedUsersResponse(BaseModel):
    users: List[AdminUserOut]
    total: int
    page: int
    page_size: int
    total_pages: int

class PaginatedListingsResponse(BaseModel):
    listings: List[AdminListingOut]
    total: int
    page: int
    page_size: int
    total_pages: int

class PaginatedReportsResponse(BaseModel):
    reports: List[AdminReportOut]
    total: int
    page: int
    page_size: int
    total_pages: int

class PaginatedVerificationsResponse(BaseModel):
    verifications: List[AdminVerificationOut]
    total: int
    page: int
    page_size: int
    total_pages: int

class AdminStatsOut(BaseModel):
    total_users: int
    verified_users: int
    new_users: int
    total_listings: int
    active_listings: int
    sold_listings: int
    new_listings: int
    total_messages: int
    active_chats: int
    recent_messages: int
    pending_reports: int
    pending_verifications: int
    blocked_users_count: int
    category_stats: List[Dict[str, Any]]
    period_days: int

class UserUpdateRequest(BaseModel):
    is_verified: Optional[bool] = None
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None
    university: Optional[str] = None

class ListingModerationRequest(BaseModel):
    status: str = Field(..., pattern="^(ACTIVE|ARCHIVED|FLAGGED|REMOVED)$")
    admin_notes: Optional[str] = None

class SystemHealthOut(BaseModel):
    database_status: str
    total_users: int
    total_listings: int
    total_messages: int
    recent_activity: Dict[str, int]
    timestamp: datetime

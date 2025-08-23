from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc, and_, or_, text
from typing import Optional, List
from datetime import datetime, timedelta

from app.api.deps import get_db, get_current_admin
from app.models.user import User
from app.models.listing import Listing
from app.models.chat import ChatMessage, BlockedUser, ChatRoom
from app.models.report import Report
from app.models.verification import Verification
from app.schemas.admin import (
    AdminUserOut, AdminListingOut, AdminStatsOut, 
    AdminReportOut, AdminVerificationOut, UserUpdateRequest,
    ListingModerationRequest, SystemHealthOut, PaginatedUsersResponse,
    PaginatedListingsResponse, PaginatedReportsResponse, PaginatedVerificationsResponse
)

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/stats", response_model=AdminStatsOut)
def get_admin_stats(
    days: int = Query(30, ge=1, le=365, description="Number of days for stats"),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Get comprehensive admin dashboard statistics"""
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # User statistics
    total_users = db.query(User).count()
    verified_users = db.query(User).filter(User.is_verified == True).count()
    new_users = db.query(User).filter(User.created_at >= cutoff_date).count() if hasattr(User, 'created_at') else 0
    
    # Listing statistics
    total_listings = db.query(Listing).count()
    active_listings = db.query(Listing).filter(Listing.status == "ACTIVE").count()
    sold_listings = db.query(Listing).filter(Listing.status == "SOLD").count()
    new_listings = db.query(Listing).filter(Listing.created_at >= cutoff_date).count()
    
    # Chat statistics
    total_messages = db.query(ChatMessage).count()
    active_chats = db.query(ChatRoom).filter(ChatRoom.status == "active").count()
    recent_messages = db.query(ChatMessage).filter(ChatMessage.timestamp >= cutoff_date).count()
    
    # Moderation statistics
    pending_reports = db.query(Report).filter(Report.status == "PENDING").count()
    pending_verifications = db.query(Verification).filter(Verification.status == "PENDING").count()
    blocked_users_count = db.query(BlockedUser).count()
    
    # Category breakdown
    category_stats = db.query(
        Listing.category,
        func.count(Listing.id).label('count')
    ).group_by(Listing.category).order_by(desc('count')).limit(10).all()
    
    return AdminStatsOut(
        total_users=total_users,
        verified_users=verified_users,
        new_users=new_users,
        total_listings=total_listings,
        active_listings=active_listings,
        sold_listings=sold_listings,
        new_listings=new_listings,
        total_messages=total_messages,
        active_chats=active_chats,
        recent_messages=recent_messages,
        pending_reports=pending_reports,
        pending_verifications=pending_verifications,
        blocked_users_count=blocked_users_count,
        category_stats=[{"category": cat[0], "count": cat[1]} for cat in category_stats],
        period_days=days
    )

@router.get("/users", response_model=PaginatedUsersResponse)  # Updated response model
def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None, description="Search by email or university"),
    verified_only: Optional[bool] = Query(None),
    admin_only: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Get paginated list of users with filtering options"""
    query = db.query(User)
    
    if search:
        query = query.filter(
            or_(
                User.email.ilike(f"%{search}%"),
                User.university_name.ilike(f"%{search}%")
            )
        )
    
    if verified_only is not None:
        query = query.filter(User.is_verified == verified_only)
    
    if admin_only is not None:
        query = query.filter(User.is_admin == admin_only)
    
    total = query.count()
    users = query.order_by(User.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return {
        "users": users,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    }

@router.patch("/users/{user_id}")
def update_user(
    user_id: str,  # Changed user_id from int to str
    update_data: UserUpdateRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Update user details (admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    return {"message": "User updated successfully", "user": AdminUserOut.from_orm(user)}

@router.delete("/users/{user_id}")
def delete_user(
    user_id: str,  # Changed user_id from int to str
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Delete a user and all associated data"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.is_admin:
        raise HTTPException(status_code=400, detail="Cannot delete admin users")
    
    # Delete associated data
    db.query(Listing).filter(Listing.owner_id == user_id).delete()
    db.query(ChatMessage).filter(
        or_(ChatMessage.sender_id == user_id, ChatMessage.receiver_id == user_id)
    ).delete()
    db.query(BlockedUser).filter(
        or_(BlockedUser.user_id == user_id, BlockedUser.blocked_by == user_id)
    ).delete()
    
    db.delete(user)
    db.commit()
    
    return {"message": "User deleted successfully"}

@router.get("/listings", response_model=PaginatedListingsResponse)  # Updated response model
def list_listings(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None, description="Filter by status"),
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search in title/description"),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Get paginated list of listings with filtering"""
    query = db.query(Listing).options(joinedload(Listing.owner))
    
    if status:
        query = query.filter(Listing.status == status)
    
    if category:
        query = query.filter(Listing.category == category)
    
    if search:
        query = query.filter(
            or_(
                Listing.title.ilike(f"%{search}%"),
                Listing.description.ilike(f"%{search}%")
            )
        )
    
    total = query.count()
    listings = query.order_by(Listing.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return {
        "listings": listings,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size  # Added missing total_pages calculation
    }

@router.patch("/listings/{listing_id}/moderate")
def moderate_listing(
    listing_id: int,
    moderation_data: ListingModerationRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Moderate a listing (approve, reject, or flag)"""
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    listing.status = moderation_data.status
    if moderation_data.admin_notes:
        # Store admin notes in metadata or create a separate admin_notes field
        pass
    
    db.commit()
    return {"message": f"Listing {moderation_data.status.lower()} successfully"}

@router.delete("/listings/{listing_id}")
def delete_listing(
    listing_id: int,
    reason: Optional[str] = Query(None, description="Reason for deletion"),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Delete a listing (admin only)"""
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    # Delete associated messages
    db.query(ChatMessage).filter(ChatMessage.listing_id == listing_id).delete()
    
    db.delete(listing)
    db.commit()
    
    return {"message": "Listing deleted successfully", "reason": reason}

@router.get("/reports", response_model=PaginatedReportsResponse)  # Updated response model
def list_reports(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None, description="Filter by status"),
    report_type: Optional[str] = Query(None, description="Filter by report type"),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Get paginated list of reports"""
    query = db.query(Report).options(
        joinedload(Report.reporter),
        joinedload(Report.reported_user),
        joinedload(Report.listing)
    )
    
    if status:
        query = query.filter(Report.status == status)
    
    if report_type:
        query = query.filter(Report.report_type == report_type)
    
    total = query.count()
    reports = query.order_by(Report.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return {
        "reports": reports,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size  # Added missing total_pages calculation
    }

@router.patch("/reports/{report_id}/resolve")
def resolve_report(
    report_id: int,
    resolution: str = Query(..., description="Resolution action taken"),
    notes: Optional[str] = Query(None, description="Admin notes"),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Resolve a report"""
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    report.status = "RESOLVED"
    report.resolution = resolution
    report.admin_notes = notes
    report.resolved_at = datetime.utcnow()
    report.resolved_by = admin.id
    
    db.commit()
    return {"message": "Report resolved successfully"}

@router.get("/verifications", response_model=PaginatedVerificationsResponse)  # Updated response model
def list_verifications(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Get paginated list of verification requests"""
    query = db.query(Verification).options(joinedload(Verification.user))
    
    if status:
        query = query.filter(Verification.status == status)
    
    total = query.count()
    verifications = query.order_by(Verification.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return {
        "verifications": verifications,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size  # Added missing total_pages calculation
    }

@router.patch("/verifications/{verification_id}/review")
def review_verification(
    verification_id: int,
    approved: bool = Query(..., description="Whether to approve or reject"),
    notes: Optional[str] = Query(None, description="Admin notes"),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Review a verification request"""
    verification = db.query(Verification).filter(Verification.id == verification_id).first()
    if not verification:
        raise HTTPException(status_code=404, detail="Verification not found")
    
    verification.status = "APPROVED" if approved else "REJECTED"
    verification.admin_notes = notes
    verification.reviewed_at = datetime.utcnow()
    verification.reviewed_by = admin.id
    
    # Update user verification status
    if approved:
        user = db.query(User).filter(User.id == verification.user_id).first()
        if user:
            user.is_verified = True
    
    db.commit()
    return {"message": f"Verification {'approved' if approved else 'rejected'} successfully"}

@router.get("/system/health", response_model=SystemHealthOut)
def get_system_health(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Get system health metrics"""
    try:
        # Database connectivity test
        db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception:
        db_status = "unhealthy"
    
    # Get recent activity metrics
    recent_activity = {
        "messages_last_hour": db.query(ChatMessage).filter(
            ChatMessage.timestamp >= datetime.utcnow() - timedelta(hours=1)
        ).count(),
        "listings_last_24h": db.query(Listing).filter(
            Listing.created_at >= datetime.utcnow() - timedelta(days=1)
        ).count(),
        "active_users_last_24h": db.query(User).filter(
            User.last_login >= datetime.utcnow() - timedelta(days=1)
        ).count() if hasattr(User, 'last_login') else 0
    }
    
    return SystemHealthOut(
        database_status=db_status,
        total_users=db.query(User).count(),
        total_listings=db.query(Listing).count(),
        total_messages=db.query(ChatMessage).count(),
        recent_activity=recent_activity,
        timestamp=datetime.utcnow()
    )

@router.post("/system/maintenance")
def toggle_maintenance_mode(
    enabled: bool = Query(..., description="Enable or disable maintenance mode"),
    message: Optional[str] = Query(None, description="Maintenance message"),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Toggle system maintenance mode"""
    # This would typically update a system configuration table or cache
    # For now, we'll return a success message
    return {
        "message": f"Maintenance mode {'enabled' if enabled else 'disabled'}",
        "maintenance_message": message,
        "updated_by": admin.email,
        "timestamp": datetime.utcnow()
    }

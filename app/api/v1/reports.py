from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.api.deps import get_db, get_current_user, get_current_admin
from app.models.report import Report, ReportStatus
from app.models.listing import Listing
from app.schemas.report import ReportCreate, ReportOut
from app.services.notification_service import NotificationService
from datetime import datetime

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.post("/", response_model=ReportOut)
def create_report(
    payload: ReportCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # Require at least reported_listing_id or reported_user_id
    if not payload.reported_listing_id and not payload.reported_user_id:
        raise HTTPException(status_code=400, detail="Must report a listing or user.")

    # Validate listing existence if listing_id present
    if payload.reported_listing_id:
        listing_exists = db.query(Listing).filter(Listing.id == payload.reported_listing_id).first()
        if not listing_exists:
            raise HTTPException(status_code=400, detail="Reported listing does not exist.")

    report = Report(
        reporter_id=current_user.id,
        reported_listing_id=payload.reported_listing_id,
        reported_user_id=payload.reported_user_id,
        reason=payload.reason,
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


@router.get("/", response_model=List[ReportOut], dependencies=[Depends(get_current_admin)])
def list_reports(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=200),
):
    reports = db.query(Report).order_by(Report.created_at.desc()).offset(skip).limit(limit).all()
    return reports


@router.post("/{report_id}/action", response_model=ReportOut, dependencies=[Depends(get_current_admin)])
def review_report(
    report_id: int,
    status: ReportStatus,
    audit_log: Optional[str] = None,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    report.status = status
    report.audit_log = audit_log
    report.reviewed_by = current_admin.id
    report.reviewed_at = datetime.utcnow()
    db.commit()
    db.refresh(report)
    
    NotificationService.notify_report_reviewed(
        db=db,
        reporter_id=report.reporter_id,
        report_id=report.id,
        status=status.value,
        audit_log=audit_log
    )
    
    return report

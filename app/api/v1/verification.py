from datetime import datetime, timedelta, timezone
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user, get_current_admin
from app.core.config import settings, allowed_domains
from app.models.user import User
from app.models.verification import Verification
from app.schemas.verification import OTPVerify, VerificationRequest, AdminReviewAction
from app.utils.emailer import send_email
from app.utils.storage import save_upload
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/verification", tags=["Verification"])



@router.post("/request")
def request_verification(payload: VerificationRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    domain = payload.university_email.split("@")[-1].lower()
    if domain not in allowed_domains():
        raise HTTPException(status_code=400, detail="Email domain not allowed")
    ver = db.query(Verification).filter(Verification.user_id == user.id).first()
    now = datetime.now(timezone.utc)
    expires = now + timedelta(seconds=settings.OTP_TTL_SECONDS)
    import random
    otp = f"{random.randint(0, 999999):06d}"
    if not ver:
        ver = Verification(
            user_id=user.id,
            university_email=payload.university_email,
            student_id=payload.student_id,
            status="pending",
            otp_code=otp,
            otp_expires_at=expires,
        )
        db.add(ver)
    else:
        ver.university_email = payload.university_email
        ver.student_id = payload.student_id
        ver.status = "pending"
        ver.otp_code = otp
        ver.otp_expires_at = expires
    db.commit()
    send_email(payload.university_email, "Your OTP Code", f"Your verification code is: {otp}. It expires in {settings.OTP_TTL_SECONDS//60} minutes.")
    return {"message": "OTP sent to university email"}

@router.post("/verify-otp")
def verify_otp(payload: OTPVerify, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    ver = db.query(Verification).filter(Verification.user_id == user.id).first()
    if not ver or not ver.otp_code:
        raise HTTPException(status_code=400, detail="No verification request found")
    now = datetime.now(timezone.utc)
    if not ver.otp_expires_at or now > ver.otp_expires_at:
        raise HTTPException(status_code=400, detail="OTP expired")
    if payload.otp_code != ver.otp_code:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    ver.otp_code = None
    db.commit()
    return {"message": "OTP verified. You can now upload your ID."}

@router.post("/upload-id")
def upload_id(file: UploadFile = File(...), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    ver = db.query(Verification).filter(Verification.user_id == user.id).first()
    if not ver:
        raise HTTPException(status_code=400, detail="No verification request found")
    path = save_upload(file, subdir="ids")
    ver.id_document_url = path
    db.commit()
    return {"message": "ID uploaded. Waiting for admin review."}

@router.get("/status")
def status(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    ver = db.query(Verification).filter(Verification.user_id == user.id).first()
    return {"status": ver.status if ver else "unverified", "id_document_url": ver.id_document_url if ver else None}

@router.get("/pending")
def pending(db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    items = db.query(Verification).filter(Verification.status == "pending").all()
    return [{"user_id": v.user_id, "email": v.university_email, "student_id": v.student_id, "id_document_url": v.id_document_url} for v in items]

@router.post("/approve/{user_id}")
def approve(user_id: str, review_action: AdminReviewAction, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    ver = db.query(Verification).filter(Verification.user_id == user_id).first()
    user = db.query(User).filter(User.id == user_id).first()
    if not ver or not user:
        raise HTTPException(status_code=404, detail="Verification or user not found")
    
    ver.status = "verified"
    ver.admin_notes = review_action.admin_notes
    ver.reviewed_at = datetime.now(timezone.utc)
    user.is_verified = True
    db.commit()
    
    NotificationService.notify_verification_status(db, user_id, "APPROVED")
    
    subject = "Your Verification Has Been Approved"
    body = f"Hello {user.email},\n\nYour university email verification has been approved. You are now a verified member of Campus Exchange.\n\nThank you,\nThe Campus Exchange Team"
    send_email(user.email, subject, body) # 📧
    
    return {"message": "User verified"}

@router.post("/reject/{user_id}")
def reject(user_id: str, review_action: AdminReviewAction, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    ver = db.query(Verification).filter(Verification.user_id == user_id).first()
    
    if not ver:
        raise HTTPException(status_code=404, detail="Verification not found")
        
    user = db.query(User).filter(User.id == user_id).first() # Fetch user to get email for notification
    ver.status = "rejected"
    ver.admin_notes = review_action.admin_notes
    ver.reviewed_at = datetime.now(timezone.utc)
    db.commit()

    if user:
        NotificationService.notify_verification_status(db, user.id, "REJECTED")

    if user: # Only attempt to send email if user was found
        subject = "Your Verification Has Been Rejected"
        body = f"Hello {user.email},\n\nYour university email verification has been rejected. Please review your submission and try again if necessary.\n\nThank you,\nThe Campus Exchange Team"
        send_email(user.email, subject, body) # 📧

    return {"message": "Verification rejected"}

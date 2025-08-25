import uuid
import random
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.core.security import hash_password, verify_password, create_access_token
from app.core.config import allowed_domains
from app.models.user import User
from app.models.verification import Verification
from app.schemas.auth import (
    ForgotPasswordIn,
    LoginIn,
    ResetPasswordIn,
    Token,
    SignUpIn,
    MessageOut,
)
from app.utils.emailer import send_email

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.get("/me")
def me(user: User = Depends(get_current_user)):
    return {
        "id": user.id,
        "email": user.email,
        "is_admin": user.is_admin,
        "is_verified": user.is_verified,
        "university_name": user.university_name,
    }


@router.post("/signup", response_model=Token)
def signup(payload: SignUpIn, db: Session = Depends(get_db)):
    # Restrict by allowed domains (if file present / configured)
    domain_list = set(allowed_domains())
    email_domain = payload.email.split("@")[-1].lower()
    if domain_list and email_domain not in domain_list:
        raise HTTPException(status_code=400, detail="Email domain not allowed")

    # Unique email check
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create user
    user = User(
        id=str(uuid.uuid4()),
        email=payload.email,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name.strip(),
        university_name=payload.university_name.strip(),
        is_verified=False,
    )
    db.add(user)
    db.commit()

    # Issue access token immediately after signup (common UX)
    token = create_access_token(user.id)
    return Token(access_token=token)


@router.post("/login", response_model=Token)
def login(payload: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    # Update last login time
    user.last_login_at = datetime.now(timezone.utc)
    db.add(user)
    db.commit()

    token = create_access_token(user.id)
    return Token(access_token=token)


# ---------- OTP Password Reset Flow ----------

@router.post("/forgot-password", response_model=MessageOut)
def forgot_password(payload: ForgotPasswordIn, db: Session = Depends(get_db)):
    """
    1) Find user by email
    2) Generate 6-digit OTP
    3) Upsert into verifications with expiry (10 minutes)
    4) Email OTP (no frontend URL used)
    """
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        # Do not leak existence; but if you prefer explicit, keep 404:
        # raise HTTPException(status_code=404, detail="User not found")
        return MessageOut(message="If this email exists, an OTP has been sent.")

    # Generate 6-digit OTP
    otp = f"{random.randint(100000, 999999)}"
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)

    # Fetch or create Verification row for this user
    verification = (
        db.query(Verification)
        .filter(Verification.user_id == user.id)
        .first()
    )
    if verification is None:
        verification = Verification(
            user_id=user.id,
            university_email=user.email,  # reuse field for contact email
            student_id=user.id,           # placeholder; keep non-null
            status="pending",
        )
        db.add(verification)

    verification.otp_code = otp
    verification.otp_expires_at = expires_at
    db.commit()
    db.refresh(verification)

    # Send OTP via email
    send_email(
        to_email=user.email,
        subject="Your password reset OTP",
        body=(
            f"Hello,\n\n"
            f"Your OTP to reset the password is: {otp}\n"
            f"This OTP will expire in 10 minutes.\n\n"
            f"If you did not request this, you can ignore this email.\n"
        ),
    )

    return MessageOut(message="If this email exists, an OTP has been sent.")


@router.post("/reset-password", response_model=MessageOut)
def reset_password(payload: ResetPasswordIn, db: Session = Depends(get_db)):
    """
    1) Validate new_password == confirm_password (schema also checks)
    2) Find user by email
    3) Check OTP matches and not expired in verifications
    4) Update hashed_password; clear OTP fields
    """
    if payload.new_password != payload.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    verification = (
        db.query(Verification)
        .filter(Verification.user_id == user.id)
        .first()
    )

    if (
        not verification
        or not verification.otp_code
        or verification.otp_code != payload.otp
    ):
        raise HTTPException(status_code=400, detail="Invalid OTP")

    if not verification.otp_expires_at or verification.otp_expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="OTP expired")

    # Update password
    user.hashed_password = hash_password(payload.new_password)

    # Clear OTP
    verification.otp_code = None
    verification.otp_expires_at = None

    db.add(user)
    db.add(verification)
    db.commit()

    return MessageOut(message="Password reset successful")

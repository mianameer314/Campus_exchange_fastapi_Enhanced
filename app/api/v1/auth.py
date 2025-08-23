from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.core.security import hash_password, verify_password, create_access_token
from app.core.config import allowed_domains
from app.models.user import User
from app.schemas.auth import LoginIn, Token, SignUpIn
from datetime import datetime, timezone

router = APIRouter(prefix="/auth", tags=["Auth"])


# New response schema for signup message only
class SignupResponse(BaseModel):
    message: str


@router.get("/me")
def me(user: User = Depends(get_current_user)):
    return {
        "id": user.id,
        "email": user.email,
        "is_admin": user.is_admin,
        "is_verified": user.is_verified,
        "university_name": user.university_name  # 👈 Added
    }

@router.post("/signup", response_model=Token)
def signup(payload: SignUpIn, db: Session = Depends(get_db)):
    # Validate email domain against allowed domains from file
    domain_list = set(allowed_domains())
    email_domain = payload.email.split("@")[-1].lower()
    if domain_list and email_domain not in domain_list:
        raise HTTPException(status_code=400, detail="Email domain not allowed")

    # Create user
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        id=str(__import__("uuid").uuid4()),
        email=payload.email,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name.strip(),
        university_name=payload.university_name.strip(),
        is_verified=False
    )
    db.add(user)
    db.commit()

    return "Registration successful"

@router.post("/login", response_model=Token)
def login(payload: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    # ✅ Update last login
    user.last_login_at = datetime.now(timezone.utc)
    db.add(user)
    db.commit()

    token = create_access_token(user.id)
    return Token(access_token=token)

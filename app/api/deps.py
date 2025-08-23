from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.core.security import decode_token
from app.models.user import User

# Use HTTPBearer to show only a token field in Swagger
bearer_scheme = HTTPBearer()

# Dependency to get a DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Type annotations for cleaner reuse
TokenDep = Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)]
DbDep = Annotated[Session, Depends(get_db)]

# Get the current user from token
def get_current_user(credentials: TokenDep, db: DbDep) -> User:
    token = credentials.credentials  # Extract the raw token string
    payload = decode_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    user = db.query(User).filter(User.id == payload["sub"]).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    return user

# Ensure current user is admin
def get_current_admin(user: User = Depends(get_current_user)) -> User:
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin only")
    return user

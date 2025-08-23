# app/api/v1/reviews.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from app.api.deps import get_db, get_current_user
from app.models.review import Review
from app.models.user import User
from app.schemas.review import ReviewIn, ReviewOut

router = APIRouter(prefix="/reviews", tags=["Reviews"])

@router.post("", response_model=ReviewOut)
def leave_review(payload: ReviewIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if payload.reviewed_id == user.id:
        raise HTTPException(status_code=400, detail="You cannot review yourself")

    review = Review(
        reviewer_id=user.id,
        reviewed_id=payload.reviewed_id,
        rating=payload.rating,
        comment=payload.comment,
    )
    db.add(review)
    db.commit()
    db.refresh(review)

    # ✅ Update reviewed user's stats
    stats = db.query(
        func.avg(Review.rating).label("avg_rating"),
        func.count(Review.id).label("count_reviews")
    ).filter(Review.reviewed_id == payload.reviewed_id).first()

    reviewed_user = db.query(User).filter(User.id == payload.reviewed_id).first()
    if reviewed_user:
        reviewed_user.rating = float(stats.avg_rating or 0.0)
        reviewed_user.reviews_count = stats.count_reviews or 0
        db.add(reviewed_user)
        db.commit()

    return review

@router.get("/{user_id}", response_model=List[ReviewOut])
def get_reviews(user_id: str, db: Session = Depends(get_db)):
    return db.query(Review).filter(Review.reviewed_id == user_id).all()

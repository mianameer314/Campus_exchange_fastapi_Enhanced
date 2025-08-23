from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.api.deps import get_db, get_current_user
from app.models.favorite import Favorite
from app.models.listing import Listing
from app.schemas.favorite import FavoriteResponse
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/favorites", tags=["Favorites"])

@router.post("/{listing_id}")
def add_favorite(listing_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    fav = db.query(Favorite).filter(Favorite.user_id == user.id, Favorite.listing_id == listing_id).first()
    if fav:
        return {"status": "already_favorited"}
    fav = Favorite(user_id=user.id, listing_id=listing_id)
    db.add(fav)
    db.commit()
    
    NotificationService.notify_new_favorite(db, listing, user.id)

    return {"status": "Added To your Favorites"}

@router.delete("/{listing_id}")
def remove_favorite(listing_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    fav = db.query(Favorite).filter(Favorite.user_id == user.id, Favorite.listing_id == listing_id).first()
    if not fav:
        raise HTTPException(status_code=404, detail="Not favorited")
    db.delete(fav)
    db.commit()
    return {"status": "ok"}

@router.get("/", response_model=List[FavoriteResponse])
def list_favorites(db: Session = Depends(get_db), user=Depends(get_current_user)):
    favorites = db.query(Favorite).filter(Favorite.user_id == user.id).all()
    return favorites

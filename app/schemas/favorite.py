from pydantic import BaseModel
from datetime import datetime

class FavoriteBase(BaseModel):
    listing_id: int

class FavoriteCreate(FavoriteBase):
    pass

class FavoriteResponse(FavoriteBase):
    id: int
    user_id: str
    
    class Config:
        from_attributes = True

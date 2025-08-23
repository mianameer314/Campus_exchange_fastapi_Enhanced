from pydantic import BaseModel, field_validator
from typing import Optional, List
from decimal import Decimal


class ListingCreate(BaseModel):
    title: str
    description: str
    category: str
    price: Decimal
    images: Optional[List[str]] = None  # URLs of uploaded images

    @field_validator("images")
    @classmethod
    def clean_images(cls, v):
        return v or []


class ListingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    price: Optional[Decimal] = None
    images: Optional[List[str]] = None  # Set default to None instead of no default

    @field_validator("images")
    @classmethod
    def validate_images(cls, v):
        if v is not None:
            # Filter out placeholder values like "string" or empty strings
            filtered_images = [img for img in v if img and img.strip() and img.lower() != "string"]
            # If no valid images remain after filtering, return None to preserve existing
            if len(filtered_images) == 0:
                return None
            return filtered_images
        return v
    
    @field_validator("title", "description", "category")
    @classmethod
    def validate_strings(cls, v):
        # Convert empty strings to None to preserve existing values
        if v is not None and not v.strip():
            return None
        return v
    
    @field_validator("price")
    @classmethod
    def validate_price(cls, v):
        # Ensure price is positive if provided
        if v is not None and v <= 0:
            raise ValueError("Price must be greater than 0")
        return v


class ListingStatusPatch(BaseModel):
    status: str  # ACTIVE, SOLD, ARCHIVED


class ListingOut(BaseModel):
    id: int
    title: str
    description: str
    category: str
    price: Decimal
    images: Optional[List[str]] = None
    status: str
    owner_id: str

    class Config:
        from_attributes = True

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional, Any

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.profile import ProfileOut, ProfileUpdate, DeleteAccountIn
from app.core.security import verify_password
from app.core.config import settings
from app.utils.storage import save_upload, gen_object_key, public_url_for_key, get_s3_client

router = APIRouter(prefix="/profile", tags=["Profile"])


# -------- Get my profile --------
@router.get("/me", response_model=ProfileOut)
def get_me(user: User = Depends(get_current_user)) -> Any:
    return user


# -------- Update profile (supports file upload + partial update) --------
@router.patch("/me", response_model=ProfileOut)
async def update_me(
    full_name: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    university_name: Optional[str] = Form(None),
    student_id: Optional[str] = Form(None),
    department: Optional[str] = Form(None),
    year_of_study: Optional[int] = Form(None),
    whatsapp_number: Optional[str] = Form(None),
    bio: Optional[str] = Form(None),
    profile_picture: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Any:
    changed = False

    # ✅ Handle profile picture upload
    if profile_picture:
        if settings.STORAGE_BACKEND == "LOCAL":
            url = save_upload(profile_picture, subdir="profiles")
        elif settings.STORAGE_BACKEND == "S3":
            s3_client = get_s3_client()
            key = gen_object_key("profiles", profile_picture.filename)
            s3_client.upload_fileobj(profile_picture.file, settings.S3_BUCKET, key)
            url = public_url_for_key(key)
        else:
            raise HTTPException(status_code=500, detail="Invalid storage backend")

        user.profile_picture = url
        changed = True

    # ✅ Handle other fields (partial updates, keep untouched as is)
    field_map = {
        "full_name": full_name,
        "phone": phone,
        "university_name": university_name,
        "student_id": student_id,
        "department": department,
        "year_of_study": year_of_study,
        "whatsapp_number": whatsapp_number,
        "bio": bio,
    }

    for field, value in field_map.items():
        if value is not None:  # update only provided fields
            if isinstance(value, str):
                value = value.strip()
                value = value if value else None
            setattr(user, field, value)
            changed = True

    if changed:
        db.add(user)
        db.commit()
        db.refresh(user)

    return user


# -------- Delete account --------
@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_me(
    payload: DeleteAccountIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect password")

    db.delete(user)
    db.commit()
    return None

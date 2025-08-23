import os
import uuid
from typing import Tuple
from fastapi import UploadFile
from app.core.config import settings
import boto3  # type: ignore
from botocore.config import Config  # type: ignore


def gen_object_key(prefix: str, filename: str) -> str:
    """Generate a unique object key for storage."""
    ext = (filename.rsplit(".", 1)[-1] if "." in filename else "bin").lower()
    return f"{prefix}/{uuid.uuid4()}.{ext}"


def public_url_for_key(key: str) -> str:
    """Return public URL for stored object."""
    if settings.STORAGE_BACKEND == "S3":
        if settings.S3_PUBLIC_BASE_URL:
            base = settings.S3_PUBLIC_BASE_URL.rstrip("/")
            return f"{base}/{key}"
        return f"https://{settings.S3_BUCKET}.s3.{settings.S3_REGION}.amazonaws.com/{key}"
    return f"/uploads/{key}"


def get_s3_client():
    """Return a configured boto3 S3 client."""
    return boto3.client(
        "s3",
        region_name=settings.S3_REGION,
        aws_access_key_id=settings.S3_ACCESS_KEY,
        aws_secret_access_key=settings.S3_SECRET_KEY,
        config=Config(signature_version="s3v4"),
    )


def save_upload(file: UploadFile, subdir: str = "uploads") -> str:
    """
    Save a file either to local storage or S3 depending on STORAGE_BACKEND.
    Returns the public URL of the stored file.
    """
    key = gen_object_key(subdir, file.filename)

    print(f"[DEBUG] Saving file: {file.filename}")
    print(f"[DEBUG] Generated key: {key}")
    print(f"[DEBUG] Storage backend: {settings.STORAGE_BACKEND}")

    if settings.STORAGE_BACKEND == "S3":
        s3 = get_s3_client()
        s3.upload_fileobj(file.file, settings.S3_BUCKET, key)
        print(f"[DEBUG] Uploaded to S3: {key}")
    else:
        base = settings.UPLOAD_DIR or "./uploads"
        abs_path = os.path.join(base, key)
        print(f"[DEBUG] Upload directory: {base}")
        print(f"[DEBUG] Full file path: {abs_path}")
        
        dir_path = os.path.dirname(abs_path)
        print(f"[DEBUG] Creating directory: {dir_path}")
        os.makedirs(dir_path, exist_ok=True)
        
        file.file.seek(0)
        content = file.file.read()
        print(f"[DEBUG] File size: {len(content)} bytes")
        
        with open(abs_path, "wb") as f:
            f.write(content)
        
        if os.path.exists(abs_path):
            print(f"[DEBUG] File successfully saved to: {abs_path}")
        else:
            print(f"[DEBUG] ERROR: File was not saved to: {abs_path}")

    public_url = public_url_for_key(key)
    print(f"[DEBUG] Public URL: {public_url}")
    return public_url


def save_upload_with_key(file: UploadFile, subdir: str = "uploads") -> Tuple[str, str]:
    """
    Save file and return both (key, public_url).
    Useful if you need to store the key in DB for later S3 operations.
    """
    key = gen_object_key(subdir, file.filename)

    if settings.STORAGE_BACKEND == "S3":
        s3 = get_s3_client()
        s3.upload_fileobj(file.file, settings.S3_BUCKET, key)
    else:
        base = settings.UPLOAD_DIR or "./uploads"
        abs_path = os.path.join(base, key)
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        with open(abs_path, "wb") as f:
            f.write(file.file.read())

    return key, public_url_for_key(key)


def create_presigned_put(key: str, content_type: str, expires: int = 3600) -> str:
    """Generate a presigned PUT URL for AWS S3."""
    client = get_s3_client()
    return client.generate_presigned_url(
        "put_object",
        Params={"Bucket": settings.S3_BUCKET, "Key": key, "ContentType": content_type},
        ExpiresIn=expires,
    )

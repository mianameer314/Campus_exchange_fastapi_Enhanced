import os
from typing import List, Literal, Optional
from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    APP_NAME: str = "Campus_Exchange API"
    APP_VERSION: str = "1.0.0"
    ENV: Literal["development", "production"] = "development"

    # Database & Auth
    DATABASE_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60

    # CORS
    CORS_ORIGINS: List[str] = []

    # Admin
    ADMIN_EMAIL: str
    ADMIN_PASSWORD: str

    # Email / SMTP
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_PORT: int = 587
    MAIL_FROM_NAME: str = "Campus Exchange"
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False

    # Verification
    ALLOWED_EMAIL_DOMAINS: str = "uni.edu,college.edu,cuiatk.edu,cuiatk.edu.pk"
    OTP_TTL_SECONDS: int = 600

    # Storage
    STORAGE_BACKEND: Literal["LOCAL", "S3"] = "LOCAL"
    UPLOAD_DIR: str = "./uploads"  # used when STORAGE_BACKEND=LOCAL

    # AWS S3 settings (for production)
    S3_BUCKET: Optional[str] = None
    S3_REGION: Optional[str] = None
    S3_ACCESS_KEY: Optional[str] = None
    S3_SECRET_KEY: Optional[str] = None
    S3_PUBLIC_BASE_URL: Optional[str] = None  # e.g. https://bucket.s3.ap-south-1.amazonaws.com

    # AI Service Configuration
    AI_SERVICE_URL: str = os.getenv("AI_SERVICE_URL", "https://mlservice-production.up.railway.app")
    AI_API_KEY: str
    AI_MODEL: str = "gpt-4o-mini"  # corrected name
    AI_TIMEOUT_SECONDS: int = 30
    AI_MAX_RETRIES: int = 3
    AI_RETRY_DELAY: float = 2.0
    
    # Feature Flags for AI services
    AI_PRICE_SUGGEST_ENABLED: bool = True
    AI_DUPLICATE_CHECK_ENABLED: bool = True
    AI_RECOMMEND_ENABLED: bool = True

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors(cls, v):
        if not v:
            return []
        if isinstance(v, str):
            return [s.strip() for s in v.split(",") if s.strip()]
        if isinstance(v, list):
            return v
        return []

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        uri = self.DATABASE_URL
        if uri.startswith("postgres://"):
            uri = uri.replace("postgres://", "postgresql://", 1)
        return uri

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()


def allowed_domains() -> List[str]:
    return [
        d.strip().lower()
        for d in settings.ALLOWED_EMAIL_DOMAINS.split(",")
        if d.strip()
    ]

def allowed_domains() -> list[str]:
    """Load allowed university email domains from a file (one per line).
    Path can be overridden with ALLOWED_DOMAINS_FILE env var.
    Lines starting with # are ignored.
    """
    import os
    from pathlib import Path
    default_path = Path(__file__).resolve().parent.parent / "data" / "allowed_domains_pk.txt"
    path = Path(os.getenv("ALLOWED_DOMAINS_FILE", default_path))
    if not path.exists():
        return []
    domains: list[str] = []
    for line in path.read_text().splitlines():
        line = line.strip().lower()
        if not line or line.startswith("#"):
            continue
        domains.append(line)
    return domains

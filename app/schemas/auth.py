from pydantic import BaseModel, EmailStr, field_validator
from app.core.validation import InputValidator  # assuming your class is here


class UserCreate(BaseModel):
    email: EmailStr
    password: str

    # Run custom validation automatically
    @field_validator("email")
    def validate_email(cls, v):
        return InputValidator.validate_email(v)

    @field_validator("password")
    def validate_password(cls, v):
        return InputValidator.validate_password(v)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: str
    email: EmailStr
    is_admin: bool
    is_verified: bool


class SignUpIn(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    university_name: str

    # Same validation as UserCreate
    @field_validator("email")
    def validate_email(cls, v):
        return InputValidator.validate_email(v)

    @field_validator("password")
    def validate_password(cls, v):
        return InputValidator.validate_password(v)

class LoginIn(BaseModel):
    email: EmailStr
    password: str


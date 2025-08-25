from pydantic import BaseModel, EmailStr, field_validator
from app.core.validation import InputValidator


class UserCreate(BaseModel):
    email: EmailStr
    password: str

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

    @field_validator("email")
    def validate_email(cls, v):
        return InputValidator.validate_email(v)

    @field_validator("password")
    def validate_password(cls, v):
        return InputValidator.validate_password(v)


class LoginIn(BaseModel):
    email: EmailStr
    password: str


# ✅ Forgot Password
class ForgotPasswordIn(BaseModel):
    email: EmailStr


class ResetPasswordIn(BaseModel):
    token: str
    new_password: str
    confirm_password: str

    @field_validator("new_password")
    def validate_password(cls, v):
        return InputValidator.validate_password(v)

    @field_validator("confirm_password")
    def passwords_match(cls, v, values):
        if "new_password" in values and v != values["new_password"]:
            raise ValueError("Passwords do not match")
        return v
    
class MessageOut(BaseModel):
    message: str

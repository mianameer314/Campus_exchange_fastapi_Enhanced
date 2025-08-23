from pydantic import BaseModel, EmailStr


class VerificationRequest(BaseModel):
    university_email: EmailStr
    student_id: str

class OTPVerify(BaseModel):
    otp_code: str

class AdminReviewAction(BaseModel):
    admin_notes: str = ""

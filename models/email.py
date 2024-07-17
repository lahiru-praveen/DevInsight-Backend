from pydantic import BaseModel, EmailStr


class EmailRequest(BaseModel):
    email: EmailStr

class VerifyEmailRequest(BaseModel):
    email: str
    code: str

class CheckEmail(BaseModel):
    email: str
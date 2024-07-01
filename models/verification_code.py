from pydantic import BaseModel


class SaveVerificationCodeRequest(BaseModel):
    email: str
    verificationCode: str

class VerificationCode(BaseModel):
    email: str
    verification_code: str
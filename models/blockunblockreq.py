from pydantic import BaseModel


class BlockUnblockRequest(BaseModel):
    organization_email: str
    email: str
    action: str
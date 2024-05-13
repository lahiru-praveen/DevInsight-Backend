from pydantic import BaseModel

class Invite(BaseModel):
    email: str
    role: str
from pydantic import BaseModel

class Invite(BaseModel):
    email: str
    role: str
    
class Invite(BaseModel):
    sent_date: str
    user_email: str
    role: str
    organization_email: str
    organization_name: str
    invite_accepted : bool      
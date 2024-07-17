from pydantic import BaseModel


class MemberModel(BaseModel):
    email: str
    username: str
    role: str
    profileStatus: str
    profilePicture: str


class RoleUpdateRequest(BaseModel):
    organization_email: str
    email: str
    new_role: str
    username: str
    
    
  
    
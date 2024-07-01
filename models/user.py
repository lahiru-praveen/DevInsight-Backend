from pydantic import BaseModel
from typing import List, Optional

class User(BaseModel):
    firstName: str
    lastName: str
    username: str
    email: str
    password: str
    company: str
    role: str
    skills: Optional[List[str]]
    profileStatus: str

class User_login(BaseModel):
    email: str
    password: str

class UserProfile(BaseModel):
    firstName: str
    lastName: str
    username: str
    email: str
    company: str
    role: str
    profileStatus: str
    skills: Optional[List[str]]
    profilePicture: Optional[str] = None

class UpdateProfileStatusRequest(BaseModel):
    email: str
    profileStatus: str
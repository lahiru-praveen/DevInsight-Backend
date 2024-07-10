from pydantic import BaseModel
from typing import List, Optional

class User(BaseModel):
    firstName: str
    lastName: str
    username: str
    email: str
    password: str
    company: str
    companyEmail: str
    experience: int
    level: Optional[str]
    role: str
    skills: Optional[List[str]]
    face_encoding: Optional[List[str]]
    profileStatus: str
    profilePicture: Optional[str] = None

class User_login(BaseModel):
    email: str
    password: str

class UserProfile(BaseModel):
    firstName: str
    lastName: str
    username: str
    email: str
    company: str
    companyEmail: str
    experience: Optional[int]
    level: Optional[str]
    role: str
    profileStatus: str
    skills: Optional[List[str]]
    profilePicture: Optional[str] = None

class UpdateProfileStatusRequest(BaseModel):
    email: str
    profileStatus: str



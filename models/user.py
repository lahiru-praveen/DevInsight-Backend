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
    experience: int = 0
    role: str
    skills: Optional[List[str]]
    face_encoding: Optional[List[str]]
    profileStatus: str
    level: str = "Beginner"
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
    experience: int
    role: str
    profileStatus: str
    skills: Optional[List[str]]
    level: str
    profilePicture: Optional[str] = None
    
class UserSkills(BaseModel):
    profileStatus: str = "Active"
    role: str
    email: str
    companyEmail: str
    python: bool = False  
    javascript: bool = False  
    java: bool = False  
    html: bool = False  
    c: bool = False  
    cs: bool = False  
    cpp: bool = False  
    php: bool = False  
    ruby: bool = False  
    swift: bool = False  
    go: bool = False  
    typescript: bool = False  
    css: bool = False  
    experienced_years: int = 0
    experience: int = 0
    level: str = "Beginner"
    avgfeedback: Optional[int] = None

class FeedBackAverage(BaseModel):
    email: str
    avgfeedback: Optional[int] = None

class UpdateProfileStatusRequest(BaseModel):
    email: str
    profileStatus: str
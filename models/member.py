from pydantic import BaseModel


class MemberModel(BaseModel):
    email: str
    first_name: str
    last_name: str
    role: str
    profileStatus: str
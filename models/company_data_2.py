from pydantic import BaseModel, EmailStr, Field
from bson import ObjectId

class ObjectIdStr(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError('Invalid ObjectId')
        return str(v)

class CompanyModel(BaseModel):
    id: ObjectId = Field(default_factory=ObjectId, alias="_id")
    company_name: str
    
    admin_email: EmailStr
    company_address: str
    phone_number: str
    has_custom_domain: bool
    domain: str
    
    hash_password: str
    email_verified: bool = False
            
    class Config:
        arbitrary_types_allowed = True
from pydantic import BaseModel, EmailStr, Field
from bson import ObjectId
from datetime import datetime




class CreateCompanyModel(BaseModel):
    company_name: str
    admin_email: EmailStr
    company_address: str
    phone_number: str
    has_custom_domain: bool
    domain: str
    password: str
    logo_url: str
    email_verification_token: str = None
# class CreateCompanyModel(BaseModel):
#     company_name: str
#     admin_email: EmailStr
#     company_address: str
#     phone_number: str
#     has_custom_domain: bool
#     domain: str = None
#     password: str
#     logo_url: str = None
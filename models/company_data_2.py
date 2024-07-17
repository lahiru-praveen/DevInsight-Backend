from pydantic import BaseModel, EmailStr, Field




class CompanyModel(BaseModel):
    
    company_name: str
    admin_email: EmailStr
    company_address: str
    phone_number: str
    has_custom_domain: bool
    domain: str
    hash_password: str
    email_verified: bool = False
    logo_url: str
            

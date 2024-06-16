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
        logo_url:str
        
        

        # company_name: str
        # company_uname: str
        # admin_email: str
        # company_address: str
        # phone_number: str
        # has_custom_domain: bool
        # domain: str
        # first_name: str
        # last_name: str
        # password: str
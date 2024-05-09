from pydantic import BaseModel

class CompanyModel(BaseModel):
    company_name: str
    company_uname: str    
    company_email: str
    backup_email: str
    manager_email: str
    first_name: str
    last_name: str
    hashpassword: str
    projectDetails:str


class Create_CompanyModel(BaseModel):
    company_name: str
    company_uname: str    
    company_email: str
    backup_email: str
    manager_email: str
    first_name: str
    last_name: str
    password: str
    projectDetails:str    
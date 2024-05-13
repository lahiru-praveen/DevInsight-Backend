from pydantic import BaseModel

class CreateCompanyModel(BaseModel):
    company_name: str
    company_uname: str
    company_email: str
    backup_email: str
    manager_email: str
    first_name: str
    last_name: str
    password: str
    projectDetails: str

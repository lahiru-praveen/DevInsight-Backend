from pydantic import BaseModel

class UpdateCompanyModel(BaseModel):
    company_name: str
    company_address: str
    phone_number: str
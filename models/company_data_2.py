from pydantic import BaseModel, Field


class CompanyModel(BaseModel):
    # company_name: str
    # company_uname: str
    # company_email: str
    # backup_email: str
    # manager_email: str
    # first_name: str
    # last_name: str
    # hash_password: str
    # # projectDetails: str
        company_name: str
        company_uname: str
        admin_email: str
        company_address: str
        phone_number: str
        has_custom_domain: bool
        domain: str
        first_name: str
        last_name: str
        hash_password: str
        
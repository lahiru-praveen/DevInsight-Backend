from fastapi import APIRouter, HTTPException
from pathlib import Path
from utilis.company_data import invites,Staff
from models.company_data import Create_CompanyModel,CompanyModel
from models.invites import Invite

UPLOAD_DIR = Path("../Upload-Files")

company_main_router = APIRouter()

@company_main_router.post("/create-company", response_model = CompanyModel)
async def post_company(record: Create_CompanyModel):
    response = await create_company(record.company_name,
                                    record.company_uname,
                                    record.company_email,
                                    record.backup_email,
                                    record.manager_email,
                                    record.first_name,
                                    record.last_name,
                                    record.password,
                                    record.projectDetails)    
    if response:
        return response
    raise HTTPException(400,"something went wrong")

@company_main_router.get("/invite-table")
async def get_invite_table():
    return invites

@company_main_router.get("/active-members")
async def get_active_members():
    return Staff

@company_main_router.delete("/invites/{invite_id}")
async def delete_invite(invite_id: int):
    global invites
    invite_index = next((index for index, invite in enumerate(invites) if invite["id"] == invite_id), None)
    if invite_index is None:
        raise HTTPException(status_code=404, detail="Invite not found")
    del invites[invite_index]
    return {"message": "Invite deleted successfully"}

@company_main_router.post("/add-invite")
async def add_invite(invite: Invite):
    global invites
    new_invite = {
        "id": len(invites) + 1,
        "email": invite.email,
        "role": invite.role,
        "device": "Date"  # Setting device value as constant = laptop
    }
    invites.append(new_invite)
    return new_invite

@company_main_router.get("/")
async def get_dummy_data():
    dummy_data = [
        {"id": 1, "name": "Dummy 1"},
        {"id": 2, "name": "Dummy 2"}
    ]
    return dummy_data






import motor.motor_asyncio
from passlib.context import CryptContext
from model import CompanyModel
client = motor.motor_asyncio.AsyncIOMotorClient(
    'mongodb+srv://buwanekamara:M16A2ak47@devinsight.u2ykqij.mongodb.net/'
)

database = client.devInsight_01
compnayCollection = database.Company

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# async def create_company(account):
#     document = account
#     result = await compnayCollection.insert_one(document)
#     return document
async def create_company(company_name: str,
    company_uname: str,    
    company_email: str,
    backup_email: str,
    manager_email: str,
    first_name: str,
    last_name: str,
    password: str,
    projectDetails:str):

    hashed_password = pwd_context.hash(password)
    document ={"company_name": company_name, "company_uname": company_uname, "company_email":company_email, "backup_email": backup_email, "manager_email": manager_email, "first_name": first_name, "last_name": last_name, "hashpassword": hashed_password, "projectDetails": projectDetails}
    result = await compnayCollection.insert_one(document)
    return CompanyModel(**document, id=str(result.inserted_id))
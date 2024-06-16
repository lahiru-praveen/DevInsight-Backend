from fastapi import APIRouter, HTTPException, Query, Depends, Body,UploadFile, File, Form
from database.db import DatabaseConnector
from models.company_data_1 import CreateCompanyModel
from models.invites import Invite
from models.company_data_2 import CompanyModel
from models.updatecompany_data import UpdateCompanyModel
from models.action_result import ActionResult

db_company = DatabaseConnector("company")

company_main_router = APIRouter()

invites = [
    {"id": 1, "email": "buwanekagame@gmail.com", "role": "Quality assurance", "device": "Date"},
    {"id": 2, "email": "example2@example.com", "role": "Developer", "device": "Date"},
    {"id": 3, "email": "example3@example.com", "role": "Developer", "device": "Date"},
    {"id": 4, "email": "example4@example.com", "role": "Quality assurance", "device": "Date"}
]

# Sample hardcoded data for invite table
Staff = [
    {"id": 1, "email": "buwanekamara@gmail.com", "name": "Buwaneka_Marasinghe", "role": "Quality assuranc"},
    {"id": 2, "email": "buwanekagame@gmail.com", "name": "Lahiru Praveen", "role": "Quality assuranc"},
    {"id": 3, "email": "chamoda@example.com", "name": "Chamoda_herath", "role": "Develope"},
    {"id": 4, "email": "ramajini@example.com", "name": "Ramajini_Ganasithan", "role": "Quality assurance"},
    {"id": 5, "email": "buwaneka@example.com", "name": "Buwaneka_Marasinghe", "role": "Develope"},
    {"id": 6, "email": "lahiru@example.com", "name": "Lahiru Praveen", "role": "Quality assurance"},
    {"id": 7, "email": "chamoda@example.com", "name": "Chamoda_herath", "role": "Develope"},
    {"id": 8, "email": "ramajini@example.com", "name": "Ramajini_Ganasithan", "role": "Develope"}
]

db_company = DatabaseConnector("company")

company_main_router = APIRouter()

@company_main_router.get("/check-company-email")
async def check_company_email(email: str = Query(...)):
    existing_email = await db_company.check_email(email)
    if existing_email:
        return {"exists": True}
    return {"exists": False}

@company_main_router.get("/check-company-username")
async def check_company_username(username: str = Query(...)):
    existing_username = await db_company.check_username(username)
    if existing_username:
        return {"exists": True}
    return {"exists": False}

@company_main_router.post("/create-company")
async def post_company(record: CreateCompanyModel):
    action_result1 = await db_company.create_company(record)  # Pass the Pydantic model instance
    print(action_result1)

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

# @company_main_router.get("/get-organization-data")
# async def get_organization_data(admin_email: str = Query(...)):
#     action_result = await db_company.get_company_by_admin_email(admin_email)
#     if not action_result.status:
#         raise HTTPException(status_code=404, detail=action_result.message)
#     data = {
#         "company_name": action_result.data.company_name,
#         "admin_email": action_result.data.admin_email,
#         "company_address": action_result.data.company_address,
#         "phone_number": action_result.data.phone_number,
#     }
#     return data
#last change

@company_main_router.get("/get-organization-data")
async def get_organization_data(admin_email: str = Query(...)):
    action_result = await db_company.get_company_by_admin_email(admin_email)
    if not action_result.status:
        raise HTTPException(status_code=404, detail=action_result.message)
    data = {
        "company_name": action_result.data.company_name,
        "admin_email": action_result.data.admin_email,
        "company_address": action_result.data.company_address,
        "phone_number": action_result.data.phone_number,
        "logo_url": action_result.data.logo_url  # Make sure logo_url is included
    }
    return data

@company_main_router.put("/update-company")
async def update_company(admin_email: str, update_data: UpdateCompanyModel):
    action_result = await db_company.update_company_by_email(admin_email, update_data)
    if not action_result.status:
        raise HTTPException(status_code=400, detail=action_result.message)
    return action_result
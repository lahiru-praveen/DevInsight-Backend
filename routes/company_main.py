from fastapi import APIRouter, HTTPException, Query, Depends, Body,UploadFile, File, Form
from passlib.context import CryptContext
from database.db import DatabaseConnector
from models.company_data_1 import CreateCompanyModel
from models.invites import Invite
from models.company_data_2 import CompanyModel
from models.updatecompany_data import UpdateCompanyModel
from models.action_result import ActionResult
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
import binascii
from config import config
from pymongo.errors import ServerSelectionTimeoutError
import motor.motor_asyncio
from fastapi.staticfiles import StaticFiles
from datetime import timedelta
import os
from fastapi.responses import JSONResponse, RedirectResponse

from models.user import User_login
from utilis.profile import verify_password, create_access_token

db_company = DatabaseConnector("company")

company_main_router = APIRouter()


@company_main_router.get("/check-company-email")
async def check_company_email(email: str):
    email_exists = await db_company.check_email_exists(email)
    return {"exists": email_exists}

@company_main_router.get("/check-company-username")
async def check_company_username(username: str = Query(...)):
    existing_username = await db_company.check_username(username)
    if existing_username:
        return {"exists": True}
    return {"exists": False}

@company_main_router.post("/create-company")
async def post_company(record: CreateCompanyModel):
    action_result1 = await db_company.create_company(record)
    if action_result1.status:
        return {"message": action_result1.message, "data": str(action_result1.data)}
    else:
        raise HTTPException(status_code=400, detail=action_result1.message)

# @company_main_router.get("/verify-email")
# async def verify_email(token: str):
#     try:
#         serializer = URLSafeTimedSerializer(config.Configurations.secret_key)
#         email = serializer.loads(token, salt='email-confirm-salt', max_age=3600)

#         result = await db_company.update_email_verification(email)
#         if result.status:
#             return {"message": "Email verified successfully"}
#         else:
#             await db_company.delete_company_by_email(email)
#             raise HTTPException(status_code=400, detail=result.message)
#     except (SignatureExpired, BadSignature):
#         await db_company.delete_company_by_email(email)
#         raise HTTPException(status_code=400, detail="Invalid or expired token")
@company_main_router.get("/verify-email")
async def verify_email(token: str):
    try:
        serializer = URLSafeTimedSerializer(config.Configurations.secret_key)
        email = serializer.loads(token, salt='email-confirm-salt', max_age=3600)

        result = await db_company.update_email_verification(email)
        if result.status:
            return RedirectResponse(url="http://localhost:5173/successpage", status_code=302)
        else:
            await db_company.delete_company_by_email(email)
            return RedirectResponse(url="http://localhost:5173/invalidpage", status_code=302)
    except (SignatureExpired, BadSignature):
        await db_company.delete_company_by_email(email)
        return RedirectResponse(url="http://localhost:5173/invalidpage", status_code=302)

@company_main_router.get("/")
async def get_dummy_data():
    dummy_data = [
        {"id": 1, "name": "Dummy 1"},
        {"id": 2, "name": "Dummy 2"}
    ]
    return dummy_data

company_main_router.mount("/assets", StaticFiles(directory="assets"), name="assets")

@company_main_router.post("/upload-logo")
async def upload_logo(admin_email: str = Form(...), file: UploadFile = File(...)):
        assets_dir = "assets"
        if not os.path.exists(assets_dir):
            os.makedirs(assets_dir)

        file_path = os.path.join(assets_dir, file.filename)
        try:
            with open(file_path, "wb") as buffer:
                buffer.write(await file.read())

            logo_url = f"/{file_path}"  # Ensure this matches your file structure
            update_data = UpdateCompanyModel(logo_url=logo_url)
            action_result = await db_company.update_company_by_email(admin_email, update_data)
            if not action_result.status:
                raise HTTPException(status_code=400, detail=action_result.message)

            return JSONResponse(content={"logo_url": logo_url}, status_code=200)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")
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
        "logo_url": action_result.data.logo_url  
    }
    return data

@company_main_router.put("/update-company")
async def update_company(admin_email: str, update_data: UpdateCompanyModel):
    action_result = await db_company.update_company_by_email(admin_email, update_data)
    if not action_result.status:
        raise HTTPException(status_code=400, detail=action_result.message)
    return action_result


@company_main_router.get("/get-organizations-with-custom-domain")
async def get_organizations_with_custom_domain():
    result = await db_company.get_organizations_with_custom_domain()
    if result.status:
        return JSONResponse(status_code=200, content={"data": result.data, "message": result.message})
    else:
        return JSONResponse(status_code=500, content={"message": result.message})

@company_main_router.post("/login-organization")
async def login(organization: User_login):

    existing_user = await db_company.get_organization_by_email(organization.email)
    if existing_user:
        # Check if 'password' key exists in existing_user
        if "hash_password" in existing_user and verify_password(organization.password, existing_user["hash_password"]):
            access_token_expires = timedelta(minutes=config.Configurations.ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"email": organization.email}, expires_delta=access_token_expires
            )
            return {
                "message": "Login successful",
                "access_token_manager": access_token,
                "token_type": "bearer",
                "email": organization.email,
            }
        else:
            raise HTTPException(status_code=401, detail="Incorrect email or password")
    else:
        raise HTTPException(status_code=404, detail="Organization not found")


@company_main_router.get("/get-organization-image")
async def get_organization_image(organization_email:str):
    try:
        result = await db_company.get_organization_image_by_email(organization_email)   
        if result.status:
            return result.data
        else:
            raise HTTPException(status_code=500, detail=result.message)
    except Exception as e:
        print(f"Error in get organization name: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    
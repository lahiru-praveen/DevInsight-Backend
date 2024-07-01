from fastapi import APIRouter, HTTPException, Query, Depends, Body,UploadFile, File, Form
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
import os
from fastapi.responses import JSONResponse

db_company = DatabaseConnector("company")

company_main_router = APIRouter()




# @company_main_router.get("/check-company-email")
# async def check_company_email(email: str):
#     email_exists = await db_company.check_email_exists(email)
#     return {"exists": email_exists}

# @company_main_router.get("/check-company-username")
# async def check_company_username(username: str = Query(...)):
#     existing_username = await db_company.check_username(username)
#     if existing_username:
#         return {"exists": True}
#     return {"exists": False}

# @company_main_router.post("/create-company")
# async def post_company(record: CreateCompanyModel):
#     action_result1 = await db_company.create_company(record)  # Pass the Pydantic model instance
#     print(action_result1)

# @company_main_router.get("/verify-email")
# async def verify_email(token: str):
#     try:
#         serializer = URLSafeTimedSerializer(config.Configurations.secret_key)
#         email = serializer.loads(token, salt='email-confirm-salt', max_age=3600)

#         # Update email verification status in the database
#         result = await db_company.update_email_verification(email)

#         if result.status:
#             return {"message": "Email verified successfully"}
#         else:
#             raise HTTPException(status_code=400, detail=result.message)

#     except (SignatureExpired, BadSignature):
#         raise HTTPException(status_code=400, detail="Invalid or expired token")
##ok for last night
# @company_main_router.get("/check-company-email")
# async def check_company_email(email: str):
#     email_exists = await db_company.check_email_exists(email)
#     return {"exists": email_exists}
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
            
#             raise HTTPException(status_code=400, detail=result.message)
#     except (SignatureExpired, BadSignature):
#         raise HTTPException(status_code=400, detail="Invalid or expired token")
@company_main_router.get("/verify-email")
async def verify_email(token: str):
    try:
        serializer = URLSafeTimedSerializer(config.Configurations.secret_key)
        email = serializer.loads(token, salt='email-confirm-salt', max_age=3600)

        result = await db_company.update_email_verification(email)
        if result.status:
            return {"message": "Email verified successfully"}
        else:
            await db_company.delete_company_by_email(email)
            raise HTTPException(status_code=400, detail=result.message)
    except (SignatureExpired, BadSignature):
        await db_company.delete_company_by_email(email)
        raise HTTPException(status_code=400, detail="Invalid or expired token")

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
# @company_main_router.post("/create-company")
# async def create_company_verification(record: CreateCompanyModel):
#     email = record.admin_email
    
#     # Generate token and send verification email
#     serializer = URLSafeTimedSerializer(config.Configurations.secret_key)
#     verification_token = serializer.dumps(email, salt='email-confirm-salt')
    
#     await db_company.send_verification_email(email, verification_token)
    
#     # Return message to inform the user to verify email
#     return {"message": "Verification email sent. Please verify your email to complete registration."}

# @company_main_router.get("/verify-email")
# async def verify_email(token: str, email: str):
#     serializer = URLSafeTimedSerializer(config.Configurations.secret_key)
#     try:
#         verified_email = serializer.loads(token, salt='email-confirm-salt', max_age=3600)
#         print(verified_email)
#         if verified_email != email:
#             raise HTTPException(status_code=400, detail="Invalid token or email")

#         # Save the company data after successful email verification
#         action_result = await db_company.update_email_verification(email)
#         if action_result.status:
#             return {"message": "Email verified successfully. Please complete your registration by submitting your details."}
#         else:
#             raise HTTPException(status_code=400, detail=action_result.message)

#     except (SignatureExpired, BadSignature):
#         raise HTTPException(status_code=400, detail="Invalid or expired token")

# @company_main_router.post("/save-company-data")
# async def save_company_data(record: CreateCompanyModel):
#     action_result = await db_company.save_company_data(record)
#     if not action_result.status:
#         raise HTTPException(status_code=400, detail=action_result.message)
#     return {"message": action_result.message}
    

# before changes
# @company_main_router.post("/create-company", response_model=ActionResult)
# async def create_company(record: CreateCompanyModel):
#     return await db_company.create_company(record)

# @company_main_router.get("/verify-email", response_model=ActionResult)
# async def verify_email(token: str):
#     action_result = ActionResult(status=True)
#     try:
#         # Verify the token
#         serializer = URLSafeTimedSerializer(config.Configurations.secret_key)  # Replace with your secret key
#         admin_email = serializer.loads(token, max_age=3600)  # Token expires in 1 hour (adjust as needed)

#         # Update email_verified field in the database
#         await db_company.verify_email(admin_email)
        
#         action_result.message = "Email verified successfully."
#     except Exception as e:
#         action_result.status = False
#         action_result.message = f"Failed to verify email: {str(e)}"
#     finally:
#         return action_result

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



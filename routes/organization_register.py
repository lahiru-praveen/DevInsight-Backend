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
from pydantic import BaseModel, EmailStr

class EmailRequest(BaseModel):
    email: EmailStr
db_company = DatabaseConnector("company")

organization_register_router = APIRouter()


@organization_register_router.post("/initiate-registration")
async def initiate_registration(email_request: EmailRequest):
    try:
        email = email_request.email
        serializer = URLSafeTimedSerializer(config.Configurations.secret_key)
        verification_token = serializer.dumps(email, salt='email-confirm-salt')

        await db_company.send_verification_email(email, verification_token)

        return {"message": "Verification email sent! Please check your email."}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to send verification email.")
    
    
@organization_register_router.post("/complete-registration")    
async def complete_registration(record: CreateCompanyModel, token: str):
    try:
        serializer = URLSafeTimedSerializer(config.Configurations.secret_key)
        email = serializer.loads(token, salt='email-confirm-salt', max_age=3600)
        if email != record.admin_email:
            raise HTTPException(status_code=400, detail="Invalid email verification")

        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        hashed_password = pwd_context.hash(record.password)

        company_entity = CompanyModel(
            company_name=record.company_name,
            admin_email=record.admin_email,
            company_address=record.company_address,
            phone_number=record.phone_number,
            has_custom_domain=record.has_custom_domain,
            domain=record.domain,
            hash_password=hashed_password,
            email_verified=True,
            logo_url=record.logo_url,
            email_verification_token=token
        )

        company_dict = company_entity.dict(by_alias=True)
        result = await db_company.__collection.insert_one(company_dict)

        return {"message": "Registration successful"}
    except (SignatureExpired, BadSignature):
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))    
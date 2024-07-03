from fastapi import APIRouter, HTTPException, FastAPI, Depends
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from database.db import DatabaseConnector
from pydantic import BaseModel
from models.action_result import ActionResult
from config import config
from models.invites import Invite

invite_main_router = APIRouter()

invite_db = DatabaseConnector("invites")
organization_db = DatabaseConnector("company")


serializer = URLSafeTimedSerializer(config.Configurations.secret_key)

from pydantic import BaseModel

@invite_main_router.get("/get-invitations")
async def get_invitations(organization_email: str):
    action_result = await invite_db.get_invitations_by_organization_email(organization_email)
    if action_result.status:
        return {"invitations": action_result.data}
    else:
        raise HTTPException(status_code=404, detail=action_result.message)

@invite_main_router.post("/send-invite")
async def send_invite(invite: Invite):
    invite_data = invite.dict()
    action_result = await invite_db.send_invite(invite_data)
    if action_result.status:
        return {"message": action_result.message, "invite_id": str(action_result.data)}
    else:
        raise HTTPException(status_code=400, detail=action_result.message)

@invite_main_router.post("/resend-invite/{invite_id}")
async def resend_invite(invite_id: str):
    action_result = await invite_db.resend_invite(invite_id)
    if action_result.status:                                
        return {"message": action_result.message}
    else:
        raise HTTPException(status_code=404, detail=action_result.message)

@invite_main_router.delete("/delete-invite/{invite_id}")
async def delete_invite(invite_id: str):
    action_result = await invite_db.delete_invite(invite_id)
    if action_result.status:
        return {"message": action_result.message}
    else:
        raise HTTPException(status_code=404, detail=action_result.message)

@invite_main_router.get("/get-invitation-details")
async def get_invitation_details(token: str):
    try:
        data = serializer.loads(token, salt='invitation_salt', max_age=3600)
        return {
            "email": data["email"],
            "organization_email": data["organization_email"],
            "organization_name" : data["organization_name"],
            "role": data["role"]
        }
    except SignatureExpired:
        raise HTTPException(status_code=400, detail="Token expired")
    except BadSignature:
        raise HTTPException(status_code=400, detail="Invalid token")
    
@invite_main_router.get("/get-organization-name")
async def get_organization_name(organization_email:str):
    try:
        result = await organization_db.get_organization_name_by_email(organization_email)   
        if result.status:
            return result.data
        else:
            raise HTTPException(status_code=500, detail=result.message)
    except Exception as e:
        print(f"Error in get organization name: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
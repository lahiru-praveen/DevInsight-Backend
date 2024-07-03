from fastapi import APIRouter, HTTPException, FastAPI, Depends
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from database.db import DatabaseConnector
from pydantic import BaseModel
from models.action_result import ActionResult
from config import config

invite_main_router = APIRouter()

db_company = DatabaseConnector("invites")

serializer = URLSafeTimedSerializer(config.Configurations.secret_key)

from pydantic import BaseModel

class Invite(BaseModel):
    sent_date: str
    user_email: str
    role: str
    organization_email: str
    organization_name: str
    invite_accepted : bool


@invite_main_router.get("/get-invitations")
async def get_invitations(organization_email: str):
    action_result = await db_company.get_invitations_by_organization_email(organization_email)
    if action_result.status:
        return {"invitations": action_result.data}
    else:
        raise HTTPException(status_code=404, detail=action_result.message)

@invite_main_router.post("/send-invite")
async def send_invite(invite: Invite):
    invite_data = invite.dict()
    action_result = await db_company.send_invite(invite_data)
    if action_result.status:
        return {"message": action_result.message, "invite_id": str(action_result.data)}
    else:
        raise HTTPException(status_code=400, detail=action_result.message)

@invite_main_router.post("/resend-invite/{invite_id}")
async def resend_invite(invite_id: str):
    action_result = await db_company.resend_invite(invite_id)
    if action_result.status:                                
        return {"message": action_result.message}
    else:
        raise HTTPException(status_code=404, detail=action_result.message)

@invite_main_router.delete("/delete-invite/{invite_id}")
async def delete_invite(invite_id: str):
    action_result = await db_company.delete_invite(invite_id)
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
    
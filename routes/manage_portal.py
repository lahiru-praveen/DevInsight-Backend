from fastapi import APIRouter, HTTPException
from database.db import DatabaseConnector
from pydantic import BaseModel
from models.action_result import ActionResult
from models.blockunblockreq import BlockUnblockRequest
from models.member import RoleUpdateRequest


# Initialize FastAPI router
manage_portal_router = APIRouter()
member_db = DatabaseConnector("user")
skill_db = DatabaseConnector("user-skills")




@manage_portal_router.get("/get-members-by-organization-email/{organization_email}")
async def get_members_by_organization_email(organization_email: str):
    try:
        
        action_result = await member_db.get_members_by_organization_email(organization_email)
        
        
        if action_result.status:
            
            return action_result.data
        else:
           
            raise HTTPException(status_code=404, detail=action_result.message)
    
    except Exception as e:
       
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    
@manage_portal_router.put("/update-member-role")
async def update_member_role(role_update_request: RoleUpdateRequest):
    try:
        organization_email = role_update_request.organization_email
        email = role_update_request.email
        new_role = role_update_request.new_role
        username = role_update_request.username
        
        

        
        action_result = await member_db.update_member_role(organization_email, email, new_role)
        action_result2 = await skill_db.update_member_role(organization_email, email, new_role)

        
        if action_result.status and action_result2.status:
            
            await member_db.send_changerole_email(username, email, new_role)

            
            return {"message": action_result.message}
        else:
            
            raise HTTPException(status_code=404, detail=action_result.message)
    
    except HTTPException as e:
        
        raise e
    
    except Exception as e:
        
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@manage_portal_router.put("/block-unblock-member")
async def block_unblock_member(request: BlockUnblockRequest):
    try:
        organization_email = request.organization_email
        email = request.email
        action = request.action
        
        
        if action not in ['block', 'unblock']:
            raise HTTPException(status_code=400, detail="Invalid action. Must be 'block' or 'unblock'.")
        
        # Call the asynchronous function from DatabaseConnector to update member profile status
        action_result = await member_db.block_unblock_member(organization_email, email, action)
        action_result2 = await skill_db.block_unblock_member(organization_email, email, action)
        
       
        if action_result.status == action_result2.status:
          
            return {"message": action_result.message}
        else:
           
            raise HTTPException(status_code=404, detail=action_result.message)
    
    except HTTPException as e:
        # Re-raise HTTPException to ensure correct status code and message propagation
        raise e
    
    except Exception as e:
        
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    
 
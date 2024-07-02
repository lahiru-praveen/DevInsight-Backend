from fastapi import APIRouter, HTTPException
from database.db import DatabaseConnector
from pydantic import BaseModel
from models.action_result import ActionResult
from models.blockunblockreq import BlockUnblockRequest
# Assuming DatabaseConnector is imported correctly and initialized as db_company
db_company = DatabaseConnector("Members")

# Initialize FastAPI router
manage_portal_router = APIRouter()

class RoleUpdateRequest(BaseModel):
    organization_email: str
    first_name:str
    last_name:str
    
    email: str
    new_role: str


       

# Define route function using path parameter
@manage_portal_router.get("/get-members-by-organization-email/{organization_email}")
async def get_members_by_organization_email(organization_email: str):
    try:
        # Call the asynchronous function from DatabaseConnector
        action_result = await db_company.get_members_by_organization_email(organization_email)
        
        # Check if operation was successful
        if action_result.status:
            # Return data if successful
            return action_result.data
        else:
            # Raise HTTPException with 404 status code and error message
            raise HTTPException(status_code=404, detail=action_result.message)
    
    except Exception as e:
        # Handle unexpected errors gracefully
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    
@manage_portal_router.put("/update-member-role")
async def update_member_role(role_update_request: RoleUpdateRequest):
    try:
        organization_email = role_update_request.organization_email
        email = role_update_request.email
        new_role = role_update_request.new_role
        first_name = role_update_request.first_name
        last_name = role_update_request.last_name

        # Call the asynchronous function from DatabaseConnector to update member role
        action_result = await db_company.update_member_role(organization_email, email, new_role)

        # Check if operation was successful
        if action_result.status:
            # Call the send_changerole_email function
            await db_company.send_changerole_email(first_name, last_name, email, new_role)

            # Return success message if successful
            return {"message": action_result.message}
        else:
            # Raise HTTPException with 404 status code and error message
            raise HTTPException(status_code=404, detail=action_result.message)
    
    except HTTPException as e:
        # Re-raise HTTPException to ensure correct status code and message propagation
        raise e
    
    except Exception as e:
        # Handle unexpected errors gracefully
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@manage_portal_router.put("/block-unblock-member")
async def block_unblock_member(request: BlockUnblockRequest):
    try:
        organization_email = request.organization_email
        email = request.email
        action = request.action
        
        # Validate action
        if action not in ['block', 'unblock']:
            raise HTTPException(status_code=400, detail="Invalid action. Must be 'block' or 'unblock'.")
        
        # Call the asynchronous function from DatabaseConnector to update member profile status
        action_result = await db_company.block_unblock_member(organization_email, email, action)
        
        # Check if operation was successful
        if action_result.status:
            # Return success message if successful
            return {"message": action_result.message}
        else:
            # Raise HTTPException with 404 status code and error message
            raise HTTPException(status_code=404, detail=action_result.message)
    
    except HTTPException as e:
        # Re-raise HTTPException to ensure correct status code and message propagation
        raise e
    
    except Exception as e:
        # Handle unexpected errors gracefully
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    
    
# @manage_portal_router.put("/update-member-role")
# async def update_member_role(role_update_request: RoleUpdateRequest):
#     try:
#         organization_email = role_update_request.organization_email
#         email = role_update_request.email
#         new_role = role_update_request.new_role

#         # Call the asynchronous function from DatabaseConnector
#         action_result = await db_company.update_member_role(organization_email, email, new_role)

#         # Check if operation was successful
#         if action_result.status:
#             # Return success message if successful
#             return {"message": action_result.message}
#         else:
#             # Raise HTTPException with 404 status code and error message
#             raise HTTPException(status_code=404, detail=action_result.message)
    
#     except HTTPException as e:
#         # Re-raise HTTPException to ensure correct status code and message propagation
#         raise e
    
#     except Exception as e:
#         # Handle unexpected errors gracefully
#         raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
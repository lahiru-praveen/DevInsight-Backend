from fastapi import APIRouter, HTTPException, UploadFile, File, Body
from database.db import DatabaseConnector
import os

from models.email import VerifyEmailRequest
from models.user import UpdateProfileStatusRequest
from models.verification_code import SaveVerificationCodeRequest
from utilis.profile import verify_password_reset, hash_password, verify_password_reset_settings

profile_settings_router = APIRouter()
user_db = DatabaseConnector("user")
verify_db = DatabaseConnector("verify-code")
organization_db = DatabaseConnector("company")


@profile_settings_router.put("/api/update_profile_status")
async def update_profile_status(profile_data: dict):
    email = profile_data.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")
    await user_db.save_user_profile(email, profile_data)
    return {"message": "Profile status updated successfully"}

@profile_settings_router.post("/api/profile/{email}/picture")
async def upload_profile_picture(email: str, file: UploadFile = File(...)):
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Invalid file type")
    file_path = f"assets/profile_pictures/{email}.jpg"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "wb") as image:
        image.write(file.file.read())
    return {"message": "Profile picture uploaded successfully"}

@profile_settings_router.post("/api/change-password")
async def change_password(email: str = Body(...), code: str = Body(...), new_password: str = Body(...)):
    # Verify the email and verification code
    if verify_password_reset(email, code):
        # Update the user's password in the database
        hashed_password = hash_password(new_password)
        await user_db.update_password(email, hashed_password)
        return {"message": "Password changed successfully"}
    else:
        raise HTTPException(status_code=400, detail="Invalid email or verification code")
    
@profile_settings_router.post("/api/change-password-organization")
async def change_password(email: str = Body(...), code: str = Body(...), new_password: str = Body(...)):
    # Verify the email and verification code
    if verify_password_reset(email, code):
        # Update the user's password in the database
        hashed_password = hash_password(new_password)
        await organization_db.update_password_organizaiton(email, hashed_password)
        return {"message": "Password changed successfully"}
    else:
        raise HTTPException(status_code=400, detail="Invalid email or verification code")    

@profile_settings_router.post("/api/change-password-settings")
async def change_password(email: str = Body(...), new_password: str = Body(...)):
    # Verify the email and verification code
    if verify_password_reset_settings(email):
        # Update the user's password in the database
        hashed_password = hash_password(new_password)
        await user_db.update_password(email, hashed_password)
        return {"message": "Password changed successfully"}
    else:
        raise HTTPException(status_code=400, detail="Invalid email or verification code")


@profile_settings_router.post("/save-verification-code")
async def save_verification_code(request: SaveVerificationCodeRequest):
    await verify_db.save_verification_code(request)

@profile_settings_router.post("/verify-email")
async def verify_email(request: VerifyEmailRequest):
    code = await verify_db.get_verify_code(request)
    if code and code == request.code:
        return {"success": True}
    else:
        raise HTTPException(status_code=400, detail="Invalid verification code")

@profile_settings_router.post("/api/reset-password")
async def reset_password(email: str = Body(...), code: str = Body(...)):
    # Implement the password reset logic here
    # For now, we're just simulating a successful response
    return {"message": "Password reset successfully!"}

@profile_settings_router.put("/update_profile_status")
async def update_profile_status(request: UpdateProfileStatusRequest):
    try:
        result = await user_db.update_user_status(request)
        if result.modified_count == 1:
            return {"message": "Profile status updated successfully"}, 200
        else:
            return {"message": "User not found"}, 404
    except Exception as e:
        return {"error": str(e)}, 500





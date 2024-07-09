from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from database.db import DatabaseConnector
from models.user import User, User_login, UserSkills
import logging
from utilis.profile import create_access_token, verify_password, get_current_user, oauth2_scheme
from datetime import timedelta
from config import config
from utilis.profile import hash_password

profile_router = APIRouter()
user_db = DatabaseConnector("user")
user_db = DatabaseConnector("user")
skill_db = DatabaseConnector("user-skills")


@profile_router.post("/signup")
async def signup(user: User):
    try:
        # Check if the user already exists
        user_entity = await user_db.get_user_by_email(user.email)
        if user_entity:
            raise HTTPException(status_code=400, detail="User already exists")

        # Hash the user's password
        hashed_password = hash_password(user.password)
        user.password = hashed_password

        # Add the user profile to the database
        await user_db.add_user_profile(user)
        
        additional_data = UserSkills(
            profileStatus=user.profileStatus,
            role=user.role,
            email=user.email,
            companyEmail=user.companyEmail
        )
        
        
        await skill_db.add_user_skills(additional_data)


        # Create an access token
        access_token_expires = timedelta(minutes=config.Configurations.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"email": user.email}, expires_delta=access_token_expires
        )

        return {
            "message": "User signed up successfully",
            "access_token": access_token,
            "token_type": "bearer"
        }

    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        logging.error(f"Error signing up: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@profile_router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await user_db.authenticate_user(form_data.username, form_data.password)
    if user:
        access_token_expires = timedelta(minutes=config.Configurations.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"email": user["email"]}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
    else:
        raise HTTPException(status_code=401, detail="Incorrect email or password")

@profile_router.post("/login")
async def login(user: User_login):
    existing_user = await user_db.get_user_by_email(user.email)
    if existing_user:
        # Check if 'password' key exists in existing_user
        if "password" in existing_user and verify_password(user.password, existing_user["password"]):
            # Update profile status to 'Active'
            await user_db.update_user_status(user)
            access_token_expires = timedelta(minutes=config.Configurations.ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"email": user.email}, expires_delta=access_token_expires
            )
            return {
                "message": "Login successful",
                "access_token": access_token,
                "token_type": "bearer",
                "email": user.email,
            }
        else:
            raise HTTPException(status_code=401, detail="Incorrect email or password")
    else:
        raise HTTPException(status_code=404, detail="User not found")


@profile_router.post("/api/user_deactivate/{email}")
async def user_deactivate(email: str, current_user: dict = Depends(get_current_user)):
    if current_user["email"] != email:
        raise HTTPException(status_code=403, detail="Forbidden: You can only deactivate your own account")
    await user_db.deactivate_users(email)

@profile_router.delete("/api/profile_delete/{email}")
async def delete_user_profile(email: str, token: str = Depends(oauth2_scheme)):
    try:
        await user_db.delete_user_profile(email)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting user: {str(e)}")


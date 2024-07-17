import os
from pydantic import EmailStr
from fastapi import APIRouter, HTTPException, Form, UploadFile, File, Body
import shutil
import config.config
from database.db import DatabaseConnector
import face_recognition
from fastapi.responses import JSONResponse
from datetime import timedelta
import numpy as np

from utilis.profile import create_access_token

bio_metrics_router = APIRouter()
user_db = DatabaseConnector("user")

FACE_IMAGES_DIR = 'assets/faces'


@bio_metrics_router.post("/register_face")
async def register_face(email: EmailStr = Form(...), file: UploadFile = File(...)):
    # Check if user already exists
    existing_user = await user_db.get_user_by_email(email)

    # Save the uploaded image
    image_path = os.path.join(FACE_IMAGES_DIR, f"{email}.png")
    with open(image_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Load the image and encode the face
    image = face_recognition.load_image_file(image_path)
    face_encodings = face_recognition.face_encodings(image)

    if len(face_encodings) == 0:
        os.remove(image_path)
        raise HTTPException(status_code=400, detail="No face found in the image.")

    # Update or insert user data
    user_data = {
        "email": email,
        "face_encoding": face_encodings[0].tolist(),
        "image_path": image_path
    }

    if existing_user:
        # Update existing user
        await user_db.update_register_face(email,user_data)
        return JSONResponse(content={"message": "Face registered successfully"})


@bio_metrics_router.post("/login_face")
async def login_face(file: UploadFile = File(...)):
    image_path = os.path.join(FACE_IMAGES_DIR, "temp.png")

    with open(image_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    image = face_recognition.load_image_file(image_path)
    face_encodings = face_recognition.face_encodings(image)

    if len(face_encodings) == 0:
        os.remove(image_path)
        raise HTTPException(status_code=400, detail="No face found in the image.")

    input_face_encoding = face_encodings[0]
    os.remove(image_path)

    users = await user_db.login_face()
    for user in users:
        registered_face_encoding = np.array(user['face_encoding'])
        if registered_face_encoding.shape == input_face_encoding.shape:
            matches = face_recognition.compare_faces([registered_face_encoding], input_face_encoding)

            if matches[0]:
                access_token_expires = timedelta(minutes=config.config.Configurations.ACCESS_TOKEN_EXPIRE_MINUTES)
                access_token = create_access_token(
                data={"email": user["email"]}, expires_delta=access_token_expires
            )

                user_data = {
                            "access_token": access_token,
                            # "token_type": "bearer",
                            "email": user["email"],
                            "password": user["password"], 
                            "role": user["role"], 
                            "companyEmail": user["companyEmail"] 
                }
                return JSONResponse(content={"message": "Login successful", "user": user_data})

    raise HTTPException(status_code=401, detail="Face not recognized.")


@bio_metrics_router.post("/api/remove_face_data")
async def remove_face_data(email: EmailStr):
    # Fetch the user from the database
    user = await user_db.get_user_by_email(email)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get the image path
    image_path = user.get("image_path")
    
    if not image_path:
        raise HTTPException(status_code=400, detail="No face data found for this user")

    # Remove the image file
    if os.path.exists(image_path):
        os.remove(image_path)
    else:
        raise HTTPException(status_code=404, detail="Face image not found on the server")

    # Update the database
    user_data = {
        "face_encoding": None,
        "image_path": None
    }

    await user_db.update_register_face(email, user_data)

    return JSONResponse(content={"message": "Face data removed successfully"})

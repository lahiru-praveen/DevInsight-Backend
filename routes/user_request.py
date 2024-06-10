from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from database.db import DatabaseConnector
from models.action_result import ActionResult
from models import request_data

request_router = APIRouter()

request_db = DatabaseConnector("request")

@request_router.post("/request")
async def request(request_item: request_data.RequestItem):
    try:
        # Log the received data
        print("Received requestText:", request_item.requestText)

        # Save the received data to MongoDB
        action_result = await request_db.add_request(request_item)

        if action_result.status:
            return {"message": "Response saved successfully"}
        else:
            raise HTTPException(status_code=500, detail=action_result.message)
    except Exception as e:
        print(f"Error in save_response: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while saving the response")

# from fastapi import FastAPI, Request, APIRouter
# from pydantic import BaseModel
# from bson import ObjectId  # Import ObjectId for querying by ID
# from database.db import DatabaseConnector
#
# request_router = APIRouter()
#
# request_db = DatabaseConnector("request")
#
# class ResponseItem(BaseModel):
#     response_text: str
#
# @request_router.post("/api/sam/")
# async def save_response(response_item: ResponseItem):
#     # Log or print the received data
#     print("Received response_text:", response_item.response_text)
#
#     # Save the received data to MongoDB
#     await request.insert_one(response_item.dict())
#
#     # Return a success message
#     return {"message": "Response saved successfully"}

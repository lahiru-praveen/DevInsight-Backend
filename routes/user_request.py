from fastapi import APIRouter, HTTPException
from models.request_data import RequestItem  # Ensure you have this model defined in models/request_data.py
from database.db import DatabaseConnector
from models.action_result import ActionResult

request_router = APIRouter()

request_db = DatabaseConnector("request")

@request_router.post("/request")
async def request(request_item: RequestItem):
    try:
        # Log the received data
        print("Received request:", request_item)

        # Save the received data to MongoDB
        action_result = await request_db.add_request(request_item)

        if action_result.status:
            return {"message": "Response saved successfully"}
        else:
            raise HTTPException(status_code=500, detail=action_result.message)
    except Exception as e:
        print(f"Error in save_response: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while saving the response")

# retrieval_router.py
from fastapi import APIRouter, HTTPException
from models.request_data import RequestItem  # Ensure you have this model defined in models/request_data.py
from database.db import DatabaseConnector
from typing import List

retrieval_router = APIRouter()

request_db = DatabaseConnector("request")

@retrieval_router.get("/responses", response_model=List[RequestItem])
async def get_responses():
    try:
        # Retrieve data from MongoDB
        responses = await request_db.get_all_requests()

        if responses:
            return responses
        else:
            raise HTTPException(status_code=404, detail="No responses found")
    except Exception as e:
        print(f"Error in get_responses: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while retrieving the responses")

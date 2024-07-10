# retrieval_router.py
from fastapi import APIRouter, HTTPException
from models.request_data import RequestItem  # Ensure you have this model defined in models/request_data.py
from database.db import DatabaseConnector
from typing import List

retrieval_router = APIRouter()

request_db = DatabaseConnector("request")

@retrieval_router.get("/pre-responses")
async def get_all_requests(user: str = None):
    if user is None:
        raise HTTPException(status_code=422, detail="Missing query parameter: user")

    try:
        result = await request_db.get_all_codes(user)
        if result.status:
            return result.data  # Return the list of documents as JSON
        else:
            raise HTTPException(status_code=500, detail=result.message)
    except Exception as e:
        print(f"Error in get_all_requests: {e}")
        raise HTTPException(status_code=500, detail=str(e))


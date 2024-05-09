from fastapi import APIRouter, HTTPException, Response
from database.db import DatabaseConnector

submission_router = APIRouter()

db2 = DatabaseConnector("code")

@submission_router.get("/pre-sub")
async def get_all_submissions():
    try:
        result = await db2.get_all_codes()
        if result.status:
            return result.data  # Return the list of documents as JSON
        else:
            raise HTTPException(status_code=500, detail="Failed to fetch data")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

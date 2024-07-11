# retrieval_router.py
from fastapi import APIRouter, HTTPException
from database.db import DatabaseConnector
from typing import List

response_router = APIRouter()

review_db = DatabaseConnector("review")

@response_router.get("/pre-code")
async def get_code(p_id: int, user: str):
    result = await review_db.get_code_by_id(p_id, user)
    if not result.status:
        raise HTTPException(status_code=404, detail=result.message)
    return result.data


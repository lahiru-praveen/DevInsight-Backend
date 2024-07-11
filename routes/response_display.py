# retrieval_router.py
from fastapi import APIRouter, HTTPException
from models.request_data import RequestItem  # Ensure you have this model defined in models/request_data.py
from database.db import DatabaseConnector
from typing import List

response_router = APIRouter()

request_db = DatabaseConnector("request")
response_db = DatabaseConnector("response")
review_db = DatabaseConnector("review")

@response_router.get("/pre-responds")
async def get_review_by_id(p_id: int, user: str):
    result = await review_db.get_review_by_id(p_id, user)
    if not result.status:
        raise HTTPException(status_code=404, detail=result.message)
    return result.data
#
# @retrieval_router.get("/get-response")
# async def get_response(p_id: int, user: str, r_id : int):
#     result = await response_db.get_response_by_id(p_id, user, r_id)
#     if not result.status:
#         raise HTTPException(status_code=404, detail=result.message)
#     return result.data

# @retrieval_router.delete("/delete-request")
# async def delete_sub(p_id:int,user:str,r_id:int):
#     try:
#         result1 = await request_db.delete_request(p_id,user,r_id)
#         result2 = await response_db.delete_request(p_id,user,r_id)
#         if result1.status or result2.status:
#             return {"Message1": result1.message, "Message2": result2.message}
#         else:
#             raise HTTPException(status_code=500, detail=[result1.message, result2.message])
#     except Exception as e:
#         print(f"Error in delete_sub: {e}")
#         raise HTTPException(status_code=500, detail=str(e))
#
#
#

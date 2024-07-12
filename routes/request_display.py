# retrieval_router.py
from fastapi import APIRouter, HTTPException
from models.request_data import RequestItem  # Ensure you have this model defined in models/request_data.py
from database.db import DatabaseConnector
from typing import List
from models.response_data import ResponseItem,SendFeedback
retrieval_router = APIRouter()

request_db = DatabaseConnector("request")
response_db = DatabaseConnector("response")
user_skills_db = DatabaseConnector("user-skills")

@retrieval_router.get("/pre-responses")
async def get_all_requests(user: str = None):
    if user is None:
        raise HTTPException(status_code=422, detail="Missing query parameter: user")
    try:
        result = await request_db.get_all_requests(user)
        print(result)
        if result.status:
            return result.data  # Return the list of documents as JSON
        else:
            raise HTTPException(status_code=500, detail=result.message)
    except Exception as e:
        print(f"Error in get_all_requests: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@retrieval_router.get("/get-response")
async def get_response(p_id: int, user: str, r_id : int):
    result = await response_db.get_response_by_id(p_id, user, r_id)
    if not result.status:
        raise HTTPException(status_code=404, detail=result.message)
    return result.data

@retrieval_router.delete("/delete-request")
async def delete_sub(p_id: int, user: str, r_id: int):
    try:
        result1 = await request_db.delete_request(p_id, user, r_id)
        result2 = await response_db.delete_request(p_id, user, r_id)
        if result1.status or result2.status:
            return {"Message1": result1.message, "Message2": result2.message}
        else:
            raise HTTPException(status_code=500, detail=[result1.message, result2.message])
    except Exception as e:
        print(f"Error in delete_sub: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# @retrieval_router.post("/submit-feedback")
# async def update_feedback(p_id: int, user: str, r_id : int):
#     result = await response_db.update_feedback(p_id, user, r_id)
#     if not result.status:
#         raise HTTPException(status_code=404, detail=result.message)
#     return result.data
#
#
#
@retrieval_router.post("/submit-feedback")
async def update_feedback(feedback_request: SendFeedback):
    print(feedback_request)  # Log the request
    result = await response_db.update_feedback(feedback_request)
    if not result.status:
        raise HTTPException(status_code=404, detail=result.message)
    return {"message": result.message}

async def calculate_and_update_avg_feedback(qae: str):
    try:
        # Aggregation pipeline to calculate average feedback
        pipeline = [
            {"$match": {"qae": qae}},  # Filter by QAE
            {"$group": {
                "_id": "$qae",
                "avgfeedback": {"$avg": {"$ifNull": ["$feedback", 0]}}  # Handle missing feedback
            }}
        ]

        async with response_db.aggregate(pipeline) as cursor:
            async for doc in cursor:
                avg_feedback = doc.get('avgfeedback')
                if avg_feedback is not None:
                    # Convert the average feedback to an integer
                    avg_feedback_int = floor(avg_feedback)

                    # Update the average feedback in the user-skills collection
                    result = await user_skills_db.update_one(
                        {"email": qae},
                        {"$set": {"avgfeedback": avg_feedback_int}}
                    )
                    if result.matched_count == 0:
                        print(f"No existing entry found for {qae}. No update performed.")
                    else:
                        print(f"Updated avgfeedback for {qae}.")
                else:
                    print(f"No feedback data found for {qae}.")
    except Exception as e:
        print(f"Error calculating or updating average feedback: {e}")

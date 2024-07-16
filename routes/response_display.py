from fastapi import APIRouter, HTTPException
from database.db import DatabaseConnector
from datetime import datetime
from typing import List
from pydantic import BaseModel

from models.response_data import ResponseItem, ResponseData, UpdateResponseRequest
from models.request_data import UpdateRequestStatus

response_router = APIRouter()

request_db = DatabaseConnector("request")
response_db = DatabaseConnector("response")
review_db = DatabaseConnector("review")

@response_router.get("/pre-responds", response_model=List[ResponseData])
async def get_pre_responds(qae: str = None):
    # Retrieve requests by qae value
    requests = await request_db.get_requests_by_qae(qae)

    if not requests:
        raise HTTPException(status_code=404, detail="No requests found for the given QAE value")

    response_data_list = []

    # Iterate through each request and fetch matching responses
    for request in requests:
        matching_response = await response_db.get_responses_by_criteria(request.user, request.p_id, request.r_id)
        if matching_response:
            response = matching_response[0]  # Assuming only one matching response per request
            response_data = ResponseData(
                p_id=request.p_id,
                user=request.user,
                p_name=request.p_name,
                req_id=request.r_id,
                req_date=request.date,
                req_subject=request.r_subject,
                req_content=request.r_content,
                res_status=response.response_status,
                res_date=response.date,
                response_content=response.response_content,
                qae=request.qae
            )
            response_data_list.append(response_data)

    return response_data_list

@response_router.post("/save-response")
async def save_response(update_request: UpdateResponseRequest):
    try:
        # Fetch the existing response from the database
        existing_response = await response_db.get_responses_by_criteria(
            user=update_request.user,
            p_id=update_request.p_id,
            r_id=update_request.r_id
        )

        if not existing_response:
            raise HTTPException(status_code=404, detail="Response not found")

        response = existing_response[0]  # Assuming only one matching response per request

        # Update the response content, status, and date
        response_update_result = await response_db.update_response(update_request)

        if not response_update_result.status:
            raise HTTPException(status_code=500, detail=response_update_result.message)

        # Update the request status in the request_db
        request_update_status = UpdateRequestStatus(
            p_id=update_request.p_id,
            r_id=update_request.r_id,
            user=update_request.user,
            r_status="Completed"
        )

        request_update_result = await request_db.update_request_status(request_update_status)

        if not request_update_result.status:
            raise HTTPException(status_code=500, detail=request_update_result.message)

        return {"message": "Response and request status updated successfully"}

    except Exception as e:
        print(f"Error in save_response: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while updating the response and request status")


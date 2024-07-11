from fastapi import APIRouter, HTTPException
from database.db import DatabaseConnector
from typing import List

from models.response_data import ResponseItem, ResponseData

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
                response_content=response.response_content
            )
            response_data_list.append(response_data)

    return response_data_list


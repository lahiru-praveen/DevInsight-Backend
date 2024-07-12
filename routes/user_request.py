from fastapi import APIRouter, HTTPException
from models.request_data import RequestItem
from database.db import DatabaseConnector
from models.action_result import ActionResult
from models.response_data import ResponseItem
request_router = APIRouter()

request_db = DatabaseConnector("request")
response_db = DatabaseConnector("response")

@request_router.post("/request")
async def request(request_item: RequestItem):
    try:
        latest_r_id_result = await request_db.get_latest_r_id(user=request_item.user, p_id=request_item.p_id)

        if latest_r_id_result.status:
            latest_r_id = latest_r_id_result.data
        else:
            latest_r_id = request_item.r_id

        action_result_request = await request_db.add_request(request_item)

        response_item = ResponseItem(
            user=request_item.user,
            p_id=request_item.p_id,
            r_id=latest_r_id + 1,  # Use the latest r_id fetched
            response_status="Pending"
        )

        if action_result_request.status:
            action_result_response = await response_db.add_response(response_item)

            if action_result_response.status:
                return {"message": "Response saved successfully"}
            else:
                raise HTTPException(status_code=500, detail=action_result_response.message)
        else:
            raise HTTPException(status_code=500, detail=action_result_request.message)
    except Exception as e:
        print(f"Error in save_response: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while saving the response")

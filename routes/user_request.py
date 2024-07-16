from fastapi import APIRouter, HTTPException
from models.request_data import RequestItem  # Ensure this model is defined in models/request_data.py
from models.action_result import ActionResult
from models.response_data import ResponseItem
from database.db import DatabaseConnector  # Ensure these are correctly implemented
from typing import List
import pandas as pd
from routes.assign_qae import qae_model  # Import the QAEModel instance

request_router = APIRouter()

# Initialize database connectors or any other required services
request_db = DatabaseConnector("request")  # Placeholder for actual implementation
response_db = DatabaseConnector("response")  # Placeholder for actual implementation

@request_router.post("/request")
async def request(request_item: RequestItem):
    try:
        # Fetch the latest r_id for the given user and p_id
        latest_r_id_result = await request_db.get_latest_r_id(user=request_item.user, p_id=request_item.p_id)

        if latest_r_id_result.status:
            latest_r_id = latest_r_id_result.data
        else:
            latest_r_id = request_item.r_id

        # Define new QAE data based on your use case
        new_qaes = pd.DataFrame({
            'experience_years': [5, 10, 3],
            'QAE_type': [2, 3, 1],
            'feedback': [4.5, 4.8, 4.0],
            'pending_request_count': [2, 1, 3],
            'email': ['new_email_1@example.com', 'chamoherath143@gmail.com', 'new_email_3@example.com']
        })

        # Select the top QAE email based on the prediction model
        selected_qae_email = qae_model.select_top_qae(new_qaes)

        # Update the request item with the selected QAE email
        request_item.qae = selected_qae_email

        # Save the request details
        action_result_request = await request_db.add_request(request_item)

        response_item = ResponseItem(
            user=request_item.user,
            p_id=request_item.p_id,
            r_id=latest_r_id + 1,  # Use the latest r_id fetched
            response_status="Not responded",
            qae=request_item.qae
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

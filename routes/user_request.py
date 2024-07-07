from fastapi import APIRouter, HTTPException
from models.request_data import RequestItem  # Ensure you have this model defined in models/request_data.py
from database.db import DatabaseConnector
from models.action_result import ActionResult

request_router = APIRouter()

request_db = DatabaseConnector("request")

@request_router.post("/request")
async def request(request_item: RequestItem):
    try:
        # Log the received data
        print("Received request:", request_item)

        # Save the received data to MongoDB
        action_result = await request_db.add_request(request_item)

        if action_result.status:
            return {"message": "Response saved successfully"}
        else:
            raise HTTPException(status_code=500, detail=action_result.message)
    except Exception as e:
        print(f"Error in save_response: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while saving the response")

# #
# #
# # from fastapi import APIRouter, HTTPException, Depends
# # from models.request_data import RequestItem
# # from models.code_data import CodeItem  # Ensure you have this model defined
# # from database.db import DatabaseConnector
# # from pymongo import ReturnDocument
# #
# # request_router = APIRouter()
# #
# # request_db = DatabaseConnector("request")
# # code_db = DatabaseConnector("code")  # Create a separate connector for the 'code' collection
# #
# # @request_router.post("/request")
# # async def request(request_item: RequestItem):
# #     try:
# #         # Log the received data
# #         print("Received request:", request_item)
# #
# #         # Retrieve additional fields from the 'code' collection
# #         code_data = await code_db.collection.find_one(
# #             {"projectName": request_item.projectName, "fileName": request_item.fileName},
# #             {"_id": 0, "projectID": 1, "description": 1, "mode": 1}
# #         )
# #
# #         if not code_data:
# #             raise HTTPException(status_code=404, detail="Project details not found in code collection")
# #
# #         # Merge the retrieved fields with the incoming request data
# #         merged_data = {**request_item.dict(), **code_data}
# #
# #         # Save the merged data to the 'request' collection
# #         action_result = await request_db.add_request(merged_data)
# #
# #         if action_result.status:
# #             return {"message": "Response saved successfully"}
# #         else:
# #             raise HTTPException(status_code=500, detail=action_result.message)
# #     except Exception as e:
# #         print(f"Error in save_response: {e}")
# #         raise HTTPException(status_code=500, detail="An error occurred while saving the response")
# #
# @request_router.post("/request")
# async def request(request_item: RequestItem):
#     try:
#         # Retrieve additional fields from the 'code' collection
#         code_data = await get_code_data(request_item.projectID)
#
#         # Merge the data from the code collection with the incoming request data
#         merged_data = request_item.dict()
#         merged_data.update({
#             "description": code_data.description,
#             "mode": code_data.mode
#         })
#
#         # Save the merged data to the 'request' collection
#         request_collection = db.get_collection("request")
#         result = await request_collection.insert_one(merged_data)
#
#         if result.inserted_id:
#             return {"message": "Response saved successfully"}
#         else:
#             raise HTTPException(status_code=500, detail="Failed to save response")
#     except Exception as e:
#         print(f"Error in save_response: {e}")
#         raise HTTPException(status_code=500, detail="An error occurred while saving the response")

# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# #
# # # # from fastapi import APIRouter, HTTPException
# # # # from pydantic import BaseModel
# # # # from database.db import DatabaseConnector
# # # # from models.action_result import ActionResult
# # # # from models import request_data
# # # #
# # # # request_router = APIRouter()
# # # #
# # # # request_db = DatabaseConnector("request")
# # # #
# # # # @request_router.post("/request")
# # # # async def request(request_item: request_data.RequestItem):
# # # #     try:
# # # #         # Log the received data
# # # #         print("Received requestText:", request_item.requestText)
# # # #
# # # #         # Save the received data to MongoDB
# # # #         action_result = await request_db.add_request(request_item)
# # # #
# # # #         if action_result.status:
# # # #             return {"message": "Response saved successfully"}
# # # #         else:
# # # #             raise HTTPException(status_code=500, detail=action_result.message)
# # # #     except Exception as e:
# # # #         print(f"Error in save_response: {e}")
# # # #         raise HTTPException(status_code=500, detail="An error occurred while saving the response")
# # # # #
# from fastapi import FastAPI, Request, APIRouter
# from pydantic import BaseModel
# from bson import ObjectId  # Import ObjectId for querying by ID
# from database.db import DatabaseConnector
#
# request_router = APIRouter()
#
# request_db = DatabaseConnector("request")
#
# class ResponseItem(BaseModel):
#     response_text: str
#
# @request_router.post("/api/sam/")
# async def save_response(response_item: ResponseItem):
#     # Log or print the received data
#     print("Received response_text:", response_item.response_text)
#
#     # Save the received data to MongoDB
#     await request.insert_one(response_item.dict())
#
#     # Return a success message
#     return {"message": "Response saved successfully"}


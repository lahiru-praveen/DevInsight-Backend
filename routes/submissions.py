from fastapi import APIRouter, HTTPException
from database.db import DatabaseConnector
from models import code_review
from models.delete_request import DeleteRequestModel

submission_router = APIRouter()

code_db = DatabaseConnector("code")
review_db = DatabaseConnector("review")
request_db = DatabaseConnector("request")
response_db = DatabaseConnector("response")


@submission_router.get("/pre-sub")
async def get_all_submissions(user: str = None):
    if user is None:
        raise HTTPException(status_code=422, detail="Missing query parameter: user")

    try:
        result = await code_db.get_all_codes(user)
        if result.status:
            return result.data  # Return the list of documents as JSON
        else:
            raise HTTPException(status_code=500, detail=result.message)
    except Exception as e:
        print(f"Error in get_all_submissions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@submission_router.delete("/delete-sub")
async def delete_sub(delete_request: DeleteRequestModel):
    try:
        result1 = await code_db.delete_code(delete_request.entity_id, delete_request.user)
        result2 = await review_db.delete_review(delete_request.entity_id, delete_request.user)
        result3 = await request_db.delete_requests_by_submission(delete_request.entity_id, delete_request.user)
        if result1.status or result2.status:
            return {"Message1": result1.message, "Message2": result2.message, "Message3": result3.message}
        else:
            raise HTTPException(status_code=500, detail=[result1.message, result2.message, result3.message])
    except Exception as e:
        print(f"Error in delete_sub: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@submission_router.get("/get-latest-p-id")
async def get_latest_p_id(user:str):
    try:
        result = await code_db.get_latest_p_id(user)
        if result.status:
            return result.data
        else:
            raise HTTPException(status_code=500, detail=result.message)
    except Exception as e:
        print(f"Error in get_latest_p_id: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@submission_router.post("/add-review")
async def add_review(review_context: code_review.CodeReviewData):
    await review_db.add_review(review_context)

@submission_router.get("/get-review/{project_id}")
async def get_review(project_id: int, user: str):
    result = await review_db.get_review_by_id(project_id,user)
    if not result.status:
        raise HTTPException(status_code=404, detail=result.message)
    return result.data

@submission_router.get("/get-request/{project_id}")
async def get_request_by_user_id(project_id: int, user: str):
    result = await request_db.get_request_by_id_and_user(project_id,user)
    if not result.status:
        raise HTTPException(status_code=404, detail=result.message)
    return result.data

@submission_router.get("/get-response-by-p_id/{project_id}")
async def get_response_by_user_id(project_id: int, user: str):
    result = await response_db.get_response_by_id_and_user(project_id,user)
    print(result.data)
    if not result.status:
        raise HTTPException(status_code=404, detail=result.message)
    return result.data

@submission_router.get("/get-request-id/{project_id}")
async def get_request_by_id(project_id: int, user: str):
    result = await request_db.get_request_by_id(project_id,user)
    if not result.status:
        raise HTTPException(status_code=404, detail=result.message)
    req_id = result.data.get("r_id", None)
    return {"r_id": req_id}


@submission_router.get("/project-names")
async def get_all_project_names(user:str):
    try:
        result = await code_db.get_all_project_names(user)
        if result.status:
            return result.data  # Return the list of project names
        else:
            raise HTTPException(status_code=500, detail=result.message)
    except Exception as e:
        print(f"Error in get_all_project_names: {e}")
        raise HTTPException(status_code=500, detail=str(e))
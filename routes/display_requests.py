from fastapi import APIRouter, HTTPException
from database.db import DatabaseConnector
from models import code_review
from models.delete_request import DeleteRequestModel

submission_router = APIRouter()

code_db = DatabaseConnector("code")
review_db = DatabaseConnector("review")


@submission_router.get("/pre-sub")
async def get_all_submissions():
    try:
        result = await code_db.get_all_codes()
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
        result1 = await code_db.delete_code(delete_request.entity_id)
        result2 = await review_db.delete_review(delete_request.entity_id)
        if result1.status | result2.status:
            return {"Message1": result1.message,"Message2": result2.message}
        else:
            raise HTTPException(status_code=500, detail={result1.message,result2.message})
    except Exception as e:
        print(f"Error in delete_sub: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@submission_router.get("/get-latest-p-id")
async def get_latest_p_id():
    try:
        result = await code_db.get_latest_p_id()
        if result.status:
            return result.data
        else:
            raise HTTPException(status_code=500, detail=result.message)
    except Exception as e:
        print(f"Error in get_latest_p_id: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@submission_router.post("/add-review")
async def add_review(review_context: code_review.CodeReviewData):
    result = await review_db.add_review(review_context)
    print(result)

@submission_router.get("/get-review/{project_id}")
async def get_review(project_id: int):
    result = await review_db.get_review_by_id(project_id)
    if not result.status:
        raise HTTPException(status_code=404, detail=result.message)
    print(result)
    return result.data

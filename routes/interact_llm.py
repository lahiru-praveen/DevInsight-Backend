from fastapi import HTTPException, APIRouter
from database.db import DatabaseConnector
from models import code_context_data, code_review
import textwrap
import logging
from utilis.llm.optimizer import CodeReviewLLM

CHUNK_SIZE = 20000  # Adjust based on transcript length and model limits
code_db = DatabaseConnector("code")


logging.basicConfig(level=logging.INFO)

llm_router = APIRouter()

@llm_router.post("/get-review")
async def get_review(code_context: code_context_data.CodeContextData):  # Receive codeContext from the request body
    try:
        action_result = await code_db.add_code(code_context)  # Await the asynchronous call
        if not action_result.status:
            raise HTTPException(status_code=500, detail=action_result.message)

        file_content = code_context.code  # Extracting data attribute from instance

        if not file_content:
            raise HTTPException(status_code=400, detail="File content is empty or not provided")

        chunks = textwrap.wrap(file_content, width=CHUNK_SIZE)
        input_chunks = chunks

        review,suggestions,refer_link = CodeReviewLLM.get_review(input_chunks, code_context.language, code_context.description)

        if not review:
            raise HTTPException(status_code=500, detail="LLM test failed or returned empty review")

        return {"review": review, "suggestions": suggestions, "refer_link": refer_link}

    except HTTPException as http_err:
        logging.error(f"HTTP error occurred: {http_err}")
        raise http_err

    except Exception as e:
        logging.error(f"Error in get_code: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

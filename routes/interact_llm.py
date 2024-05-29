from fastapi import HTTPException, APIRouter

from database.db import DatabaseConnector
from models import code_context_data, code_review
import textwrap
from utilis.generate_response import CodeReviewLLM
import logging

CHUNK_SIZE = 20000  # Adjust based on transcript length and model limits
db1 = DatabaseConnector("code")

logging.basicConfig(level=logging.INFO)

llm_router = APIRouter()

@llm_router.post("/get_review")
async def get_review(code_context: code_context_data.CodeContextData):  # Receive codeContext from the request body
    try:
        action_result1 = await db1.add_code(code_context)  # Await the asynchronous call
        print(action_result1)

        file_content = code_context.code  # Extracting data attribute from instance

        if not file_content:
            raise HTTPException(status_code=400, detail="File content is empty or not provided")

        chunks = textwrap.wrap(file_content, width=CHUNK_SIZE)
        input_chunks = chunks

        result = CodeReviewLLM.get_review(input_chunks, code_context.language, code_context.description)

        if not result:
            raise HTTPException(status_code=500, detail="LLM test failed or returned empty result")

        print(result)
        return result

    except HTTPException as http_err:
        logging.error(f"HTTP error occurred: {http_err}")
        raise http_err

    except Exception as e:
        logging.error(f"Error in get_code: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@llm_router.post("/get_suggestions")
async def get_suggestions(review_context: code_review.CodeReviewData):  # Receive codeContext from the request body
    try:
        review_content = review_context.review
        code_content = review_context.code

        if not review_content and not code_content:
            raise HTTPException(status_code=400, detail="Review, Code content is empty or not provided")

        chunks = textwrap.wrap(code_content, width=CHUNK_SIZE)
        input_chunks = chunks

        result = CodeReviewLLM.get_suggestions(input_chunks, review_context.review)

        if not result:
            raise HTTPException(status_code=500, detail="LLM test failed or returned empty result")

        print(result)
        return result

    except HTTPException as http_err:
        logging.error(f"HTTP error occurred: {http_err}")
        raise http_err

    except Exception as e:
        logging.error(f"Error in get_code: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
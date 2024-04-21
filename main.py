import uvicorn
from fastapi import FastAPI, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from models import CodeRequest
from languageDetector import CodeLanguageDetector
import textwrap
from generateResponse import TestLLM

import logging
from models.Data import CodeContextData


UPLOAD_DIR = Path("../Upload-Files")

CHUNK_SIZE = 20000  # Adjust based on transcript length and model limits
FILE_CONTENT = ""

app = FastAPI()

logging.basicConfig(level=logging.INFO)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust as per your security requirements
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/uploadfile/")
async def create_upload_files(file_uploads: list[UploadFile]):
    saved_files = []
    for file_upload in file_uploads:
        try:
            data = await file_upload.read()
            save_to = UPLOAD_DIR / file_upload.filename
            with open(save_to, "wb") as f:
                f.write(data)
            saved_files.append(file_upload.filename)
        except IOError as e:
            return JSONResponse(status_code=500, content={"error": f"Failed to save file: {e}"})
    return {"filenames": saved_files}


@app.get("/files")
def get_files(directory: str = "../Upload-Files"):
    directory_path = Path(directory)
    files = [{"name": file.name, "size": file.stat().st_size} for file in directory_path.iterdir() if file.is_file()]
    formatted_files = [{"name": file["name"], "size": f"{file['size'] / 1024:.2f} KB"} for file in files]
    print("Files:", formatted_files)
    return formatted_files


@app.get("/files/{file_name}")
def get_file_content(file_name: str):
    global FILE_CONTENT
    file_path = UPLOAD_DIR / file_name
    try:
        with open(file_path, 'r') as file:
            content = file.read()
            FILE_CONTENT = content
        return content
    except FileNotFoundError:
        return {"error": "File not found"}


@app.post("/detect-language/")
async def detect_language(code_request: CodeRequest.CodeRequest):
    supported_languages = ["python", "javascript", "java", "csharp", "cpp", "php", "ruby", "swift", "go", "typescript", "html", "c"] 
    if code_request.language.lower() in supported_languages:
        is_language = CodeLanguageDetector.detect_language(code_request.code, code_request.language)
        if is_language:
            return 1 #{"message": "Code is in the specified language"}
        else:
            return 2 #{"message": "Code language does not match the selected language"}
    else:
        return 3 #{"error": "Unsupported language"}


@app.post("/get_code")
def get_code(codeContext: CodeContextData):  # Receive codeContext from the request body
    try:
        file_content = codeContext.data  # Extracting data attribute

        if not file_content:
            raise HTTPException(status_code=400, detail="File content is empty or not provided")

        chunks = textwrap.wrap(file_content, width=CHUNK_SIZE)
        input_chunks = chunks

        result = TestLLM.testLLM(input_chunks)

        if not result:
            raise HTTPException(status_code=500, detail="LLM test failed or returned empty result")

        return result

    except HTTPException as http_err:
        logging.error(f"HTTP error occurred: {http_err}")
        raise http_err

    except Exception as e:
        logging.error(f"Error in get_code: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")











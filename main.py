import uvicorn
from fastapi import FastAPI, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from models import CodeRequest
from test import CodeLanguageDetector

UPLOAD_DIR = Path("../Upload-Files")

app = FastAPI()

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
    file_path = UPLOAD_DIR / file_name
    try:
        with open(file_path, 'r') as file:
            content = file.read()
        return content
    except FileNotFoundError:
        return {"error": "File not found"}


@app.post("/detect-language/")
async def detect_language(code_request: CodeRequest.CodeRequest):
    supported_languages = ["python", "javascript", "java", "csharp", "cpp", "php", "ruby", "swift", "go", "typescript", "html", "c"] 
    if code_request.language.lower() in supported_languages:
        is_language = CodeLanguageDetector.detect_language(code_request.code, code_request.language)
        if is_language:
            return {"message": "Code is in the specified language"}
        else:
            return {"message": "Code language does not match the selected language"}
    else:
        return {"error": "Unsupported language"}


# @app.post("/detect-language/")
# async def detect_language(language: str, code: str ):
#     supported_languages = ["python", "javascript", "java", "csharp", "cpp", "php", "ruby", "swift", "go", "typescript", "html", "c"]
#     if language in supported_languages:
#         is_language = CodeLanguageDetector.detect_language(code, language)
#         if is_language:
#             return {"message": "Code is in the specified language"}
#         else:
#             return {"message": "Code language does not match the selected language"}
#     else:
#         return {"error": "Unsupported language"}

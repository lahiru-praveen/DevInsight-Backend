from fastapi import APIRouter, UploadFile
from pathlib import Path
from fastapi.responses import JSONResponse

UPLOAD_DIR = Path("../Upload-Files")

file_router = APIRouter()


@file_router.post("/uploadfile/")
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


@file_router.get("/files")
def get_files(directory: str = "../Upload-Files"):
    directory_path = Path(directory)
    files = [{"name": file.name, "size": file.stat().st_size} for file in directory_path.iterdir() if file.is_file()]
    formatted_files = [{"name": file["name"], "size": f"{file['size'] / 1024:.2f} KB"} for file in files]
    print("Files:", formatted_files)
    return formatted_files


@file_router.get("/files/{file_name}")
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

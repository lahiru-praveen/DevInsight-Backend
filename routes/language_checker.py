from fastapi import APIRouter
from utilis.language_detector import CodeLanguageDetector
from models import code_request

lan_check_router = APIRouter()


@lan_check_router.post("/detect-language/")
async def detect_language(code_req: code_request.CodeRequest):
    supported_languages = ["python", "javascript", "java", "csharp", "cpp", "php", "ruby", "swift", "go", "typescript",
                           "html", "c"]

    if code_req.language.lower() in supported_languages:
        try:
            is_language = CodeLanguageDetector.detect_language(code_req.code, code_req.language)
            if is_language:
                return 1  # {"message": "Code is in the specified language"}
            else:
                return 2  # {"message": "Code language does not match the selected language"}
        except Exception as e:
            # Log the unexpected error
            print(f"Unexpected error in API endpoint: {e}")
            return 3  # {"error": "Internal server error"}
    else:
        return 3  # {"error": "Unsupported language"}

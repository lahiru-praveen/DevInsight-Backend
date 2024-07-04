from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

class Configurations:
    mongo_db_url = os.getenv("MONGO_DB_URL")
    google_api_key = os.getenv("GOOGLE_API_KEY")
    secret_key = "cc4d488099b41de3c3049d005e95faff7f8e3052ceeb566a5cddae6b9ee5092f"
    SECRET_KEY = "teamlemon"
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 60
    gemini_api_key = os.getenv("GEMINI_API_KEY")
   
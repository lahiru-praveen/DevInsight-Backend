from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

class Configurations:
    mongo_db_url = os.getenv("MONGO_DB_URL")
    google_api_key = os.getenv("GOOGLE_API_KEY")
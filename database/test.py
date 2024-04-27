from pymongo import MongoClient
from fastapi import APIRouter

db_router = APIRouter()

# MongoDB connection
client = MongoClient('mongodb+srv://praveenwal21:2z9hVJq5Zoa51aqr@cluster0.q8xy9uo.mongodb.net/')
db = client['dev_insight']
collection = db['code']

@db_router.post('/get_codes')  # Change to POST method
def get_code():
    try:
        # Insert a document
        document = {"key": "123", "value": "456"}
        collection.insert_one(document)
        return 'Document inserted successfully!'

    except Exception as e:
        return f"Error: {e}"

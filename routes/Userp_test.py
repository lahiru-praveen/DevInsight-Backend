from fastapi import APIRouter, HTTPException, Query, Depends
from database.db import DatabaseConnector


db_company = DatabaseConnector("company")


Userp_test_router = APIRouter()
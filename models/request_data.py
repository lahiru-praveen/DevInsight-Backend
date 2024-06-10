from pydantic import BaseModel

class RequestItem(BaseModel):
    requestText: str

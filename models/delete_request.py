from pydantic import BaseModel

class DeleteRequestModel(BaseModel):
    entity_id: int
    user: str
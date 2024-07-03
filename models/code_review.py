from typing import Optional, Annotated
from pydantic import BaseModel, Field, BeforeValidator

PyObjectId = Annotated[str, BeforeValidator(str)]

class CodeReviewData(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    user: str  # Proper type annotation
    p_id: int = Field(...)
    code: str = Field(...)
    review: str = Field(...)
    suggestions: str = Field(...)
    reference_links: str = Field(...)

    class Config:
        arbitrary_types_allowed = True
from datetime import date
from typing import Optional
from pydantic import BaseModel, Field, BeforeValidator
from typing_extensions import Annotated

PyObjectId = Annotated[str, BeforeValidator(str)]

class CodeContextData(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    user: str = Field(...)
    p_id: int = Field(...)
    p_name: str = Field(...)
    f_name:str = Field(...)
    submission_date: str = str(date.today().strftime("%Y-%m-%d"))
    language: str = Field(...)
    description: str = Field(...)
    code: str = Field(...)
    mode: object = Field(...)





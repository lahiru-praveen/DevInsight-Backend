from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, BeforeValidator
from typing_extensions import Annotated
PyObjectId = Annotated[str, BeforeValidator(str)]



class CodeContextData(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    submission_date: str = str(date.today().strftime("%Y-%m-%d"))
    code: str
    language: str
    description: str

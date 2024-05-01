from typing import Optional

from pydantic import BaseModel, Field, BeforeValidator
from typing_extensions import Annotated

PyObjectId = Annotated[str, BeforeValidator(str)]


class CodeContextData(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    code: str
    language: str
    description: str

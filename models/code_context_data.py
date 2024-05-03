from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, BeforeValidator, validator
from typing_extensions import Annotated

PyObjectId = Annotated[str, BeforeValidator(str)]

class CodeContextData(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    p_id: str
    p_name: str
    submission_date: str = str(date.today().strftime("%Y-%m-%d"))
    language: str
    description: str
    code: str
    mode: int

    # Validator to auto-generate project ID
    # @validator("p_id", pre=True, always=True)
    # def set_auto_project_id(cls, v, values):
    #     cls._project_count += 1
    #     return cls._project_count



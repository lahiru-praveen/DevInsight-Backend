from datetime import date
from typing import Optional
from pydantic import BaseModel, Field, BeforeValidator
from typing_extensions import Annotated

PyObjectId = Annotated[str, BeforeValidator(str)]

class RequestItem(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    user : str = Field(...)
    p_id : int = Field(...)
    p_name: str = Field(...)
    r_id : int = Field(...)
    r_subject : str = Field(...)
    r_content : str = Field(...)
    qae : str = Field(...)
    r_status : str = Field(...)
    date :  str = str(date.today().strftime("%Y-%m-%d"))

class AssignItem(BaseModel):
    user : str = Field(...)
    p_id : int = Field(...)
    r_id : int = Field(...)
    qae : str = Field(...)

class AssignForwardItem(BaseModel):
    user : str = Field(...)
    p_id : int = Field(...)
    r_id : int = Field(...)
    qae : str = Field(...)

class UpdateRequestStatus(BaseModel):
    p_id: int
    r_id: int
    user: str
    r_status: str

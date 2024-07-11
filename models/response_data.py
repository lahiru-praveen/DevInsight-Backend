from datetime import date
from typing import Optional
from pydantic import BaseModel, Field, BeforeValidator
from typing_extensions import Annotated

PyObjectId = Annotated[str, BeforeValidator(str)]

class ResponseItem(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    user : str = Field(...)
    p_id : int = Field(...)
    r_id : int = Field(...)
    qae : str = Field(...)
    response_content : str = Field(...)
    feedback : int = Field(...)
    date :  str = Field(...)
    response_status : str = "Pending"

class ResponseData(BaseModel):
    p_id : int = Field(...)
    user: str = Field(...)
    p_name: str = Field(...)
    req_id: int = Field(...)
    req_date: str = Field(...)
    req_subject: str = Field(...)
    req_content: str = Field(...)
    res_status: str = Field(...)
    res_date: str = Field(...)
    response_content: str = Field(...)

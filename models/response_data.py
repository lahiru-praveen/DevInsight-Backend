from datetime import date
from typing import Optional
from pydantic import BaseModel, Field, BeforeValidator
from typing_extensions import Annotated

PyObjectId = Annotated[str, BeforeValidator(str)]

class ResponseItem(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    user: str
    p_id: int
    r_id: int
    qae: Optional[str] = ""
    response_content: Optional[str] = ""
    feedback: Optional[int] = None  # This field is optional
    date: Optional[str] = ""
    response_status: str

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
    qae: Optional[str] = ""

class SendFeedback(BaseModel):
    p_id : int = Field(...)
    user: str = Field(...)
    r_id: int = Field(...)
    feedback: int = Field(...)

class UpdateResponseRequest(BaseModel):
    p_id: int
    user: str
    r_id: int
    response_content: str


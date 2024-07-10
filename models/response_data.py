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
    date :  str = str(date.today().strftime("%Y-%m-%d"))

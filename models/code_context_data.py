from pydantic import BaseModel


class CodeContextData(BaseModel):
    data: str

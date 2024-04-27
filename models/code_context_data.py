from pydantic import BaseModel


class CodeContextData(BaseModel):
    code: str
    language: str
    description: str

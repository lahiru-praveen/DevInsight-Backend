from pydantic import BaseModel


class CodeRequest(BaseModel):
    language: str = ""
    code: str = ""



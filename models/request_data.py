# from pydantic import BaseModel
#
# class RequestItem(BaseModel):
#     requestText: str

from pydantic import BaseModel,Field

class RequestItem(BaseModel):

    projectID: int
    projectName: str
    fileName:str
    language: str
    description: str
    code: str
    review: str
    mode: object
    subjectText: str
    requestText: str

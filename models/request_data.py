# # from pydantic import BaseModel
# #
# # class RequestItem(BaseModel):
# #     requestText: str
#
# # from pydantic import BaseModel,Field
# #
# # class RequestItem(BaseModel):
# #
# #     projectID: int
# #     projectName: str
# #     fileName:str
# #     language: str
# #     description: str
# #     code: str
# #     review: str
# #     mode: object
# #     subjectText: str
# #     requestText: str
from pydantic import BaseModel, Field

class RequestItem(BaseModel):
#     projectID: int = Field(...)
    projectName: str = Field(...)
    fileName: str = Field(...)
#     language: str = Field(...)
#     description: str = Field(...)
#     mode: str = Field(...)
    code: str = Field(...)
    review: str = Field(...)
    subjectText: str = Field(...)
    requestText: str = Field(...)


from pydantic import BaseModel,BeforeValidator
from typing_extensions import Annotated

PyObjectId = Annotated[str, BeforeValidator(str)]

class CodeReviewData(BaseModel):
    code: str
    review: str
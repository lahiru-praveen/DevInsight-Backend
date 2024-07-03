from typing import Optional
from pydantic import BaseModel


class TokenData(BaseModel):
    email: Optional[str] = None
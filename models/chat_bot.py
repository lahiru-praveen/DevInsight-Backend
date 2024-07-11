from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str
    user_id: str
    
    

class CodeReviewContext(BaseModel):
    selectedFileContent: str
    reviewContent: str
    suggestionContent: str
    referLinksContent: str    
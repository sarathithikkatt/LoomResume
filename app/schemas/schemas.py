from pydantic import BaseModel

class ChatRequest(BaseModel):
    chat_id: str
    message: str
    provider: str
    model: str

class ChatResponse(BaseModel):
    response: str
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class ChatMessage(BaseModel):
    role: str  # "user" or "model"
    parts: List[str]

class ChatRequest(BaseModel):
    message: str
    conversation_history: Optional[List[Dict[str, Any]]] = None

class ChatResponse(BaseModel):
    response: str
    conversation_history: List[Dict[str, Any]]
    timestamp: str

class ChatHistoryResponse(BaseModel):
    conversation_history: List[Dict[str, Any]]
    user_id: int

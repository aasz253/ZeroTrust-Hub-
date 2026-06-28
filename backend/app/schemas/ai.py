from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime


class AIChatRequest(BaseModel):
    message: str
    conversation_id: Optional[int] = None
    context_type: Optional[str] = None
    context_id: Optional[str] = None


class AIChatResponse(BaseModel):
    response: str
    conversation_id: int
    tokens_used: Optional[int] = None


class ConversationResponse(BaseModel):
    id: int
    title: Optional[str] = None
    context_type: Optional[str] = None
    context_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ConversationMessageResponse(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True

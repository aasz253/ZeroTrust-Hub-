from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database.session import get_db
from app.models.user import User
from app.models.ai_conversation import AIConversation, AIConversationMessage
from app.core.security import get_current_user
from app.schemas.ai import AIChatRequest, AIChatResponse, ConversationResponse, ConversationMessageResponse
from app.services.ai_service import AIService

router = APIRouter(prefix="/api/ai", tags=["AI Assistant"])


@router.post("/chat", response_model=AIChatResponse)
async def chat(
    request: AIChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = AIService(db)
    result = await service.chat(
        user_id=current_user.id,
        message=request.message,
        conversation_id=request.conversation_id,
        context_type=request.context_type,
        context_id=request.context_id,
    )
    return AIChatResponse(**result)


@router.get("/conversations")
def list_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conversations = (
        db.query(AIConversation)
        .filter(AIConversation.user_id == current_user.id)
        .order_by(desc(AIConversation.updated_at))
        .all()
    )
    return [ConversationResponse.model_validate(c) for c in conversations]


@router.get("/conversations/{conversation_id}/messages")
def get_conversation_messages(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    messages = (
        db.query(AIConversationMessage)
        .join(AIConversation)
        .filter(
            AIConversation.id == conversation_id,
            AIConversation.user_id == current_user.id,
        )
        .order_by(AIConversationMessage.created_at)
        .all()
    )
    return [ConversationMessageResponse.model_validate(m) for m in messages]

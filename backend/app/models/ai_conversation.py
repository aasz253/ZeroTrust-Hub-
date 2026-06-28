from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database.session import Base


class AIConversation(Base):
    __tablename__ = "ai_conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255))
    context_type = Column(String(50))
    context_id = Column(String(100))
    metadata_json = Column(JSON)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user = relationship("User", back_populates="ai_conversations")
    messages = relationship(
        "AIConversationMessage",
        back_populates="conversation",
        order_by="AIConversationMessage.created_at",
    )


class AIConversationMessage(Base):
    __tablename__ = "ai_conversation_messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(
        Integer, ForeignKey("ai_conversations.id"), nullable=False
    )
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    metadata_json = Column(JSON)
    tokens_used = Column(Integer)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    conversation = relationship(
        "AIConversation", back_populates="messages"
    )

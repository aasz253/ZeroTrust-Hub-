from typing import Optional
from sqlalchemy.orm import Session
from app.models.ai_conversation import AIConversation, AIConversationMessage
from app.core.config import settings
import json
import httpx


class AIService:
    def __init__(self, db: Session):
        self.db = db
        self.api_key = settings.OPENAI_API_KEY or settings.GEMINI_API_KEY
        self.provider = "openai" if settings.OPENAI_API_KEY else "gemini"

    async def chat(
        self, user_id: int, message: str, conversation_id: Optional[int] = None,
        context_type: Optional[str] = None, context_id: Optional[str] = None
    ) -> dict:
        if not conversation_id:
            title = message[:100]
            conversation = AIConversation(
                user_id=user_id,
                title=title,
                context_type=context_type,
                context_id=context_id,
            )
            self.db.add(conversation)
            self.db.commit()
            self.db.refresh(conversation)
            conversation_id = conversation.id

        user_msg = AIConversationMessage(
            conversation_id=conversation_id,
            role="user",
            content=message,
        )
        self.db.add(user_msg)
        self.db.commit()

        history = (
            self.db.query(AIConversationMessage)
            .filter(AIConversationMessage.conversation_id == conversation_id)
            .order_by(AIConversationMessage.created_at)
            .all()
        )

        ai_response = await self._call_ai_api(message, history)

        assistant_msg = AIConversationMessage(
            conversation_id=conversation_id,
            role="assistant",
            content=ai_response["response"],
            tokens_used=ai_response.get("tokens_used"),
        )
        self.db.add(assistant_msg)
        self.db.commit()

        return {
            "response": ai_response["response"],
            "conversation_id": conversation_id,
            "tokens_used": ai_response.get("tokens_used"),
        }

    async def _call_ai_api(self, message: str, history: list) -> dict:
        if self.provider == "openai":
            return await self._call_openai(message, history)
        return self._fallback_response(message)

    async def _call_openai(self, message: str, history: list) -> dict:
        messages = [
            {
                "role": "system",
                "content": "You are ZeroTrust AI, a cybersecurity expert assistant. "
                "Help users with vulnerability analysis, threat intelligence, "
                "security recommendations, incident response, and secure coding. "
                "Provide detailed, accurate, and actionable security information.",
            }
        ]
        for msg in history[-10:]:
            messages.append({"role": msg.role, "content": msg.content})
        messages.append({"role": "user", "content": message})

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": "gpt-4",
                        "messages": messages,
                        "max_tokens": 2048,
                    },
                )
                data = resp.json()
                return {
                    "response": data["choices"][0]["message"]["content"],
                    "tokens_used": data.get("usage", {}).get("total_tokens"),
                }
        except Exception:
            return self._fallback_response(message)

    def _fallback_response(self, message: str) -> dict:
        return {
            "response": "I'm operating in offline mode. I can provide general cybersecurity guidance. "
            "For AI-powered analysis, please configure an OpenAI or Gemini API key in settings.\n\n"
            f"Regarding your query about '{message[:100]}': As a ZeroTrust Hub security assistant, "
            "I recommend implementing defense-in-depth strategies, following the principle of least privilege, "
            "and maintaining regular security assessments. Please configure an AI provider API key for detailed analysis.",
            "tokens_used": 0,
        }

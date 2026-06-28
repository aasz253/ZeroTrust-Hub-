from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database.session import Base


class Playbook(Base):
    __tablename__ = "playbooks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    trigger_type = Column(String(50), nullable=False)
    trigger_config = Column(JSON, default=dict)
    is_active = Column(Boolean, default=True)
    auto_run = Column(Boolean, default=False)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    actions = relationship("PlaybookAction", back_populates="playbook", cascade="all, delete-orphan")


class PlaybookAction(Base):
    __tablename__ = "playbook_actions"

    id = Column(Integer, primary_key=True, index=True)
    playbook_id = Column(Integer, ForeignKey("playbooks.id"), nullable=False)
    action_type = Column(String(50), nullable=False)
    action_config = Column(JSON, default=dict)
    order = Column(Integer, default=0)
    playbook = relationship("Playbook", back_populates="actions")


class PlaybookExecution(Base):
    __tablename__ = "playbook_executions"

    id = Column(Integer, primary_key=True, index=True)
    playbook_id = Column(Integer, ForeignKey("playbooks.id"), nullable=False)
    triggered_by = Column(String(100))
    trigger_event = Column(JSON)
    status = Column(String(20), default="pending")
    result = Column(JSON)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from datetime import datetime, timezone
from app.database.session import Base


class Setting(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(Text)
    value_type = Column(String(20), default="string")
    category = Column(String(50))
    is_encrypted = Column(Boolean, default=False)
    description = Column(String(500))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

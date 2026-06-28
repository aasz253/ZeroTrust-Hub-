from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Boolean, Float
from datetime import datetime, timezone
from app.database.session import Base


class FimEntry(Base):
    __tablename__ = "fim_entries"

    id = Column(Integer, primary_key=True, index=True)
    file_path = Column(String(1000), nullable=False, index=True)
    file_name = Column(String(255))
    status = Column(String(20), default="monitored")
    current_hash = Column(String(64))
    previous_hash = Column(String(64))
    file_size = Column(Integer)
    permissions = Column(String(20))
    owner = Column(String(100))
    last_checked = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_changed = Column(DateTime)
    change_count = Column(Integer, default=0)
    is_critical = Column(Boolean, default=False)
    tags = Column(JSON, default=list)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

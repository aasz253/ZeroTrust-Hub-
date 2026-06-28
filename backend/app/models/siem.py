from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Float
from datetime import datetime, timezone
from app.database.session import Base


class SiemLog(Base):
    __tablename__ = "siem_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    source_ip = Column(String(45))
    hostname = Column(String(255))
    facility = Column(String(50), index=True)
    severity = Column(String(20), index=True)
    program = Column(String(100))
    message = Column(Text)
    raw = Column(Text)
    tags = Column(JSON, default=list)
    correlation_id = Column(String(64))
    processed = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

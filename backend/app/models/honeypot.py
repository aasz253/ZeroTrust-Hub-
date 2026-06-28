from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Boolean
from datetime import datetime, timezone
from app.database.session import Base


class HoneypotEvent(Base):
    __tablename__ = "honeypot_events"

    id = Column(Integer, primary_key=True, index=True)
    service = Column(String(50), nullable=False)
    source_ip = Column(String(45), nullable=False)
    source_port = Column(Integer)
    destination_port = Column(Integer)
    protocol = Column(String(10), default="tcp")
    username = Column(String(255))
    password = Column(String(255))
    command = Column(Text)
    payload = Column(Text)
    raw_data = Column(Text)
    country = Column(String(100))
    is_attack = Column(Boolean, default=True)
    attack_type = Column(String(100))
    severity = Column(String(20), default="MEDIUM")
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    metadata = Column(JSON, default=dict)

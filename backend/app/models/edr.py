from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, Boolean
from datetime import datetime, timezone
from app.database.session import Base


class EdrProcess(Base):
    __tablename__ = "edr_processes"

    id = Column(Integer, primary_key=True, index=True)
    pid = Column(Integer)
    name = Column(String(255), index=True)
    exe = Column(String(500))
    cmdline = Column(Text)
    username = Column(String(100))
    cpu_percent = Column(Float)
    memory_percent = Column(Float)
    connections = Column(JSON, default=list)
    is_suspicious = Column(Boolean, default=False)
    anomaly_reason = Column(String(500))
    first_seen = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_seen = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

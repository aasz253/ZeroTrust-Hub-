from sqlalchemy import Column, Integer, String, DateTime, JSON, Boolean, Float
from datetime import datetime, timezone
from app.database.session import Base


class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String(45), nullable=False, index=True)
    hostname = Column(String(255))
    mac_address = Column(String(17))
    status = Column(String(20), default="offline")
    open_ports = Column(JSON, default=list)
    os = Column(String(100))
    os_version = Column(String(100))
    vendor = Column(String(100))
    device_type = Column(String(50))
    risk_score = Column(Float, default=0.0)
    first_seen = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_seen = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    is_active = Column(Boolean, default=True)
    tags = Column(JSON, default=list)
    notes = Column(String(500))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

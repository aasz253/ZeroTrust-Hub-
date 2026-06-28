from sqlalchemy import Column, Integer, String, DateTime, Float, Text, JSON, Boolean
from datetime import datetime, timezone
from app.database.session import Base


class Threat(Base):
    __tablename__ = "threats"

    id = Column(Integer, primary_key=True, index=True)
    indicator = Column(String(500), nullable=False, index=True)
    indicator_type = Column(
        String(50), nullable=False
    )
    threat_type = Column(String(100))
    severity = Column(String(20), index=True)
    confidence = Column(Float)
    source = Column(String(100))
    description = Column(Text)
    mitre_attack_id = Column(String(20))
    mitre_tactic = Column(String(100))
    mitre_technique = Column(String(200))
    tags = Column(JSON)
    first_seen = Column(DateTime)
    last_seen = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    is_active = Column(Boolean, default=True)
    country = Column(String(100))
    asn = Column(String(100))
    related_indicators = Column(JSON)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

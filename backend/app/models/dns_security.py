from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Boolean, Float
from datetime import datetime, timezone
from app.database.session import Base


class MaliciousDomain(Base):
    __tablename__ = "malicious_domains"

    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String(255), nullable=False, unique=True)
    threat_type = Column(String(100))
    severity = Column(String(20), default="MEDIUM")
    source = Column(String(100))
    confidence = Column(Float, default=1.0)
    is_active = Column(Boolean, default=True)
    first_seen = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_seen = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    metadata = Column(JSON, default=dict)


class DNSQuery(Base):
    __tablename__ = "dns_queries"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    source_ip = Column(String(45))
    domain = Column(String(255), nullable=False)
    query_type = Column(String(10))
    response_code = Column(String(10))
    response_ip = Column(String(45))
    is_blocked = Column(Boolean, default=False)
    is_malicious = Column(Boolean, default=False)
    threat_match = Column(String(255))
    duration_ms = Column(Float)
    raw_data = Column(Text)


class DNSBlockerRule(Base):
    __tablename__ = "dns_blocker_rules"

    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String(255), nullable=False)
    pattern_type = Column(String(20), default="exact")
    action = Column(String(20), default="block")
    category = Column(String(100))
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    hit_count = Column(Integer, default=0)
    created_by = Column(Integer)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

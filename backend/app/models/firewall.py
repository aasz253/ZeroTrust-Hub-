from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Boolean, Enum
from datetime import datetime, timezone
from app.database.session import Base
import enum


class RuleAction(str, enum.Enum):
    ALLOW = "allow"
    BLOCK = "block"
    RATE_LIMIT = "rate_limit"


class RuleDirection(str, enum.Enum):
    INBOUND = "inbound"
    OUTBOUND = "outbound"
    FORWARD = "forward"


class RuleProtocol(str, enum.Enum):
    TCP = "tcp"
    UDP = "udp"
    ICMP = "icmp"
    ANY = "any"


class FirewallRule(Base):
    __tablename__ = "firewall_rules"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    action = Column(String(20), nullable=False)
    direction = Column(String(20), default="inbound")
    protocol = Column(String(10), default="any")
    source_ip = Column(String(45))
    destination_ip = Column(String(45))
    source_port = Column(Integer)
    destination_port = Column(Integer)
    interface = Column(String(50))
    priority = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    is_system = Column(Boolean, default=False)
    log_hits = Column(Boolean, default=False)
    hit_count = Column(Integer, default=0)
    created_by = Column(Integer)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    extra_data = Column(JSON, default=dict)

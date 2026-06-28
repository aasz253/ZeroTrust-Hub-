from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float
from datetime import datetime, timezone
from app.database.session import Base


class GeoIPRule(Base):
    __tablename__ = "geoip_rules"

    id = Column(Integer, primary_key=True, index=True)
    country_code = Column(String(10), nullable=False)
    country_name = Column(String(255), nullable=False)
    action = Column(String(20), default="block")
    notes = Column(Text)
    is_active = Column(Boolean, default=True)
    hit_count = Column(Integer, default=0)
    created_by = Column(Integer)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class GeoIPCache(Base):
    __tablename__ = "geoip_cache"

    id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String(45), nullable=False, unique=True)
    country_code = Column(String(10))
    country_name = Column(String(255))
    city = Column(String(255))
    isp = Column(String(255))
    latitude = Column(Float)
    longitude = Column(Float)
    is_blocked = Column(Boolean, default=False)
    checked_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime)


class GeoIPHit(Base):
    __tablename__ = "geoip_hits"

    id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String(45), nullable=False)
    country_code = Column(String(10))
    country_name = Column(String(255))
    action = Column(String(20))
    path = Column(String(500))
    user_agent = Column(Text)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

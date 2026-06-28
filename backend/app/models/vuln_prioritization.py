from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Boolean, Float
from datetime import datetime, timezone
from app.database.session import Base


class VulnPriority(Base):
    __tablename__ = "vuln_priorities"

    id = Column(Integer, primary_key=True, index=True)
    cve_id = Column(String(50), nullable=False, unique=True)
    cvss_score = Column(Float)
    cvss_severity = Column(String(20))
    epss_score = Column(Float)
    epss_percentile = Column(Float)
    is_cisa_kev = Column(Boolean, default=False)
    cisa_date_added = Column(DateTime)
    combined_score = Column(Float)
    priority_tier = Column(String(20))
    exploit_maturity = Column(String(50))
    has_ransomware = Column(Boolean, default=False)
    affected_vendor = Column(String(255))
    affected_product = Column(String(255))
    description = Column(Text)
    recommendations = Column(JSON)
    last_updated = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    metadata = Column(JSON, default=dict)

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database.session import Base


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(500), nullable=False)
    report_type = Column(String(50), nullable=False)
    format = Column(String(20), default="pdf")
    status = Column(String(20), default="draft")
    severity = Column(String(20))
    summary = Column(Text)
    executive_summary = Column(Text)
    technical_findings = Column(JSON)
    risk_assessment = Column(JSON)
    recommendations = Column(JSON)
    report_data = Column(JSON)
    file_path = Column(String(1000))
    generated_at = Column(DateTime)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user = relationship("User")

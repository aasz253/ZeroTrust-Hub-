from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Boolean, Float
from datetime import datetime, timezone
from app.database.session import Base


class SSLCertificate(Base):
    __tablename__ = "ssl_certificates"

    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String(255), nullable=False, unique=True)
    port = Column(Integer, default=443)
    issuer = Column(String(500))
    subject = Column(String(500))
    serial_number = Column(String(255))
    fingerprint_sha256 = Column(String(255))
    valid_from = Column(DateTime)
    valid_to = Column(DateTime)
    days_remaining = Column(Integer)
    is_expired = Column(Boolean, default=False)
    is_expiring_soon = Column(Boolean, default=False)
    is_self_signed = Column(Boolean, default=False)
    is_wildcard = Column(Boolean, default=False)
    weak_cipher = Column(Boolean, default=False)
    protocol_version = Column(String(20))
    cipher_suite = Column(String(100))
    certificate_chain = Column(JSON)
    dns_names = Column(JSON)
    ocsp_url = Column(String(500))
    revocation_status = Column(String(50))
    errors = Column(JSON)
    status = Column(String(20), default="valid")
    last_checked = Column(DateTime)
    next_check = Column(DateTime)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    extra_data = Column(JSON, default=dict)

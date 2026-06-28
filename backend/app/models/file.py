from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database.session import Base


class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    original_name = Column(String(500), nullable=False)
    stored_name = Column(String(500), nullable=False)
    file_path = Column(String(1000), nullable=False)
    file_size = Column(BigInteger)
    mime_type = Column(String(100))
    hash_sha256 = Column(String(64))
    hash_md5 = Column(String(32))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

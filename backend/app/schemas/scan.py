from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ScanCreate(BaseModel):
    target: str
    scan_type: str
    ports: Optional[str] = None


class ScanResponse(BaseModel):
    id: int
    target: str
    scan_type: str
    status: str
    progress: int
    severity: Optional[str] = None
    findings_count: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class VulnerabilityResponse(BaseModel):
    id: int
    cve_id: str
    title: str
    description: str
    severity: str
    cvss_score: float
    affected_vendor: Optional[str] = None
    affected_product: Optional[str] = None
    published_date: Optional[datetime] = None
    remediation: Optional[str] = None

    class Config:
        from_attributes = True

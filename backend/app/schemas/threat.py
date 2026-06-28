from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime


class ThreatResponse(BaseModel):
    id: int
    indicator: str
    indicator_type: str
    threat_type: Optional[str] = None
    severity: str
    confidence: Optional[float] = None
    source: Optional[str] = None
    description: Optional[str] = None
    mitre_attack_id: Optional[str] = None
    mitre_tactic: Optional[str] = None
    mitre_technique: Optional[str] = None
    is_active: bool
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ThreatSummary(BaseModel):
    total: int
    critical: int
    high: int
    medium: int
    low: int
    by_type: dict[str, int]
    by_source: dict[str, int]

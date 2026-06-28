from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class DeviceResponse(BaseModel):
    id: int
    ip_address: str
    hostname: Optional[str] = None
    mac_address: Optional[str] = None
    status: Optional[str] = "offline"
    open_ports: Optional[list] = []
    os: Optional[str] = None
    os_version: Optional[str] = None
    vendor: Optional[str] = None
    device_type: Optional[str] = None
    risk_score: Optional[float] = 0.0
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    is_active: bool = True
    tags: Optional[list] = []
    notes: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class NetworkStats(BaseModel):
    total_devices: int
    online_count: int
    offline_count: int
    suspicious_count: int
    open_ports_total: int
    risk_score_avg: float

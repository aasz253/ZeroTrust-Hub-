from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime


class DashboardStats(BaseModel):
    threat_score: int
    active_alerts: int
    critical_vulnerabilities: int
    devices_online: int
    security_health: int
    total_scans: int
    total_threats: int
    total_vulnerabilities: int
    recent_activities: list[dict]
    vulnerability_severity: dict[str, int]
    threat_types: dict[str, int]
    scan_history: list[dict]
    top_threats: list[dict]
    ai_recommendations: list[str]

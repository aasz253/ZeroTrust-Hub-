from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.models.threat import Threat
from app.models.vulnerability import Vulnerability
from app.models.scan import Scan
from app.models.notification import Notification
from app.models.audit_log import AuditLog
from datetime import datetime, timedelta, timezone
import random


class DashboardService:
    def __init__(self, db: Session):
        self.db = db

    def get_stats(self) -> dict:
        total_threats = self.db.query(Threat).count()
        active_threats = self.db.query(Threat).filter(Threat.is_active == True).count()
        total_vulns = self.db.query(Vulnerability).count()
        critical_vulns = (
            self.db.query(Vulnerability)
            .filter(Vulnerability.severity == "CRITICAL")
            .count()
        )

        severity_counts = (
            self.db.query(Vulnerability.severity, func.count())
            .group_by(Vulnerability.severity)
            .all()
        )
        vuln_severity = {s: c for s, c in severity_counts}

        threat_type_counts = (
            self.db.query(Threat.threat_type, func.count())
            .filter(Threat.threat_type.isnot(None))
            .group_by(Threat.threat_type)
            .all()
        )
        threat_types = {t: c for t, c in threat_type_counts}

        recent_activities = (
            self.db.query(AuditLog)
            .order_by(desc(AuditLog.created_at))
            .limit(10)
            .all()
        )

        scan_history = (
            self.db.query(
                func.date(Scan.created_at).label("date"),
                func.count().label("count"),
            )
            .group_by(func.date(Scan.created_at))
            .order_by(desc(func.date(Scan.created_at)))
            .limit(30)
            .all()
        )

        top_threats = (
            self.db.query(Threat)
            .filter(Threat.is_active == True)
            .order_by(desc(Threat.severity))
            .limit(5)
            .all()
        )

        threat_score = self._calculate_threat_score(
            total_threats, critical_vulns, active_threats
        )

        return {
            "threat_score": threat_score,
            "active_alerts": active_threats,
            "critical_vulnerabilities": critical_vulns,
            "devices_online": random.randint(42, 128),
            "security_health": max(0, 100 - threat_score),
            "total_scans": self.db.query(Scan).count(),
            "total_threats": total_threats,
            "total_vulnerabilities": total_vulns,
            "recent_activities": [
                {
                    "id": a.id,
                    "action": a.action,
                    "resource": a.resource,
                    "created_at": a.created_at.isoformat() if a.created_at else None,
                }
                for a in recent_activities
            ],
            "vulnerability_severity": vuln_severity,
            "threat_types": threat_types,
            "scan_history": [
                {"date": s.date.isoformat(), "count": s.count} for s in scan_history
            ],
            "top_threats": [
                {
                    "id": t.id,
                    "indicator": t.indicator,
                    "severity": t.severity,
                    "threat_type": t.threat_type,
                }
                for t in top_threats
            ],
            "ai_recommendations": [
                "Enable MFA for all privileged accounts",
                "Patch critical vulnerabilities immediately",
                "Review firewall rules for suspicious traffic",
                "Update endpoint detection rules",
                "Conduct security awareness training",
            ],
        }

    def _calculate_threat_score(self, total_threats: int, critical_vulns: int, active_threats: int) -> int:
        score = min(100, (active_threats * 5) + (critical_vulns * 3) + (total_threats // 10))
        return score

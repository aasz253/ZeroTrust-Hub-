from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Optional
from app.database.session import get_db
from app.models.threat import Threat
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.threat import ThreatResponse, ThreatSummary

router = APIRouter(prefix="/api/threats", tags=["Threats"])


@router.get("")
def list_threats(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    severity: Optional[str] = Query(None),
    indicator_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(Threat)
    if severity:
        q = q.filter(Threat.severity == severity.upper())
    if indicator_type:
        q = q.filter(Threat.indicator_type == indicator_type)

    total = q.count()
    items = (
        q.order_by(desc(Threat.last_seen))
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return {
        "items": [ThreatResponse.model_validate(t) for t in items],
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size,
    }


@router.get("/summary")
def threat_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    severity_counts = (
        db.query(Threat.severity, func.count())
        .group_by(Threat.severity)
        .all()
    )
    type_counts = (
        db.query(Threat.indicator_type, func.count())
        .group_by(Threat.indicator_type)
        .all()
    )
    source_counts = (
        db.query(Threat.source, func.count())
        .filter(Threat.source.isnot(None))
        .group_by(Threat.source)
        .all()
    )

    return {
        "total": db.query(Threat).count(),
        "critical": dict(severity_counts).get("CRITICAL", 0),
        "high": dict(severity_counts).get("HIGH", 0),
        "medium": dict(severity_counts).get("MEDIUM", 0),
        "low": dict(severity_counts).get("LOW", 0),
        "by_type": dict(type_counts),
        "by_source": dict(source_counts),
    }

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional
from datetime import datetime, timezone
from app.database.session import get_db
from app.models.user import User
from app.models.siem import SiemLog
from app.core.security import get_current_user

router = APIRouter(prefix="/api/siem", tags=["SIEM"])


@router.get("/logs")
def list_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    severity: Optional[str] = Query(None),
    source_ip: Optional[str] = Query(None),
    program: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(SiemLog)

    if severity:
        q = q.filter(SiemLog.severity == severity.upper())
    if source_ip:
        q = q.filter(SiemLog.source_ip == source_ip)
    if program:
        q = q.filter(SiemLog.program == program)
    if search:
        q = q.filter(SiemLog.message.ilike(f"%{search}%"))
    if start_date:
        try:
            dt = datetime.fromisoformat(start_date)
            q = q.filter(SiemLog.timestamp >= dt)
        except ValueError:
            pass
    if end_date:
        try:
            dt = datetime.fromisoformat(end_date)
            q = q.filter(SiemLog.timestamp <= dt)
        except ValueError:
            pass

    total = q.count()
    items = q.order_by(desc(SiemLog.timestamp)).offset((page - 1) * page_size).limit(page_size).all()
    pages = max(1, (total + page_size - 1) // page_size)

    severities = (
        db.query(SiemLog.severity, SiemLog.severity)
        .distinct()
        .order_by(SiemLog.severity)
        .all()
    )

    return {
        "items": [
            {
                "id": l.id,
                "timestamp": l.timestamp.isoformat() if l.timestamp else None,
                "source_ip": l.source_ip,
                "hostname": l.hostname,
                "facility": l.facility,
                "severity": l.severity,
                "program": l.program,
                "message": l.message[:500] if l.message else "",
                "raw": l.raw[:1000] if l.raw else "",
                "tags": l.tags or [],
            }
            for l in items
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": pages,
        "severities": [s[0] for s in severities],
    }


@router.get("/logs/{log_id}")
def get_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    log = db.query(SiemLog).filter(SiemLog.id == log_id).first()
    if not log:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Log not found")
    return {
        "id": log.id,
        "timestamp": log.timestamp.isoformat() if log.timestamp else None,
        "source_ip": log.source_ip,
        "hostname": log.hostname,
        "facility": log.facility,
        "severity": log.severity,
        "program": log.program,
        "message": log.message,
        "raw": log.raw,
        "tags": log.tags or [],
    }


@router.get("/stats")
def siem_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from sqlalchemy import func
    total = db.query(SiemLog).count()
    last_hour = db.query(SiemLog).filter(
        SiemLog.timestamp >= datetime.now(timezone.utc)
    ).count()
    severity_counts = (
        db.query(SiemLog.severity, func.count(SiemLog.id))
        .group_by(SiemLog.severity)
        .all()
    )
    top_ips = (
        db.query(SiemLog.source_ip, func.count(SiemLog.id).label("cnt"))
        .group_by(SiemLog.source_ip)
        .order_by(desc("cnt"))
        .limit(10)
        .all()
    )
    return {
        "total_logs": total,
        "last_hour": last_hour,
        "severity_distribution": dict(severity_counts),
        "top_source_ips": [{"ip": ip, "count": cnt} for ip, cnt in top_ips if ip],
    }

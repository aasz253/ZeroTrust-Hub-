from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional
from app.database.session import SessionLocal, get_db
from app.models.honeypot import HoneypotEvent
from app.models.user import User
from app.core.security import get_current_user
from app.services import honeypot_service
from pydantic import BaseModel

router = APIRouter(prefix="/api/honeypot", tags=["Honeypot"])


class HoneypotConfig(BaseModel):
    port: int
    service: str


@router.get("/events")
def list_events(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    service: Optional[str] = Query(None),
    source_ip: Optional[str] = Query(None),
    attack_type: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(HoneypotEvent)
    if service:
        q = q.filter(HoneypotEvent.service == service)
    if source_ip:
        q = q.filter(HoneypotEvent.source_ip == source_ip)
    if attack_type:
        q = q.filter(HoneypotEvent.attack_type == attack_type)
    if severity:
        q = q.filter(HoneypotEvent.severity == severity)

    total = q.count()
    items = q.order_by(desc(HoneypotEvent.timestamp)).offset((page - 1) * page_size).limit(page_size).all()
    return {
        "items": [
            {
                "id": e.id,
                "service": e.service,
                "source_ip": e.source_ip,
                "source_port": e.source_port,
                "destination_port": e.destination_port,
                "username": e.username,
                "attack_type": e.attack_type,
                "severity": e.severity,
                "timestamp": e.timestamp.isoformat() if e.timestamp else None,
                "country": e.country,
            }
            for e in items
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/events/{event_id}")
def get_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    event = db.query(HoneypotEvent).filter(HoneypotEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return {
        "id": event.id,
        "service": event.service,
        "source_ip": event.source_ip,
        "source_port": event.source_port,
        "destination_port": event.destination_port,
        "protocol": event.protocol,
        "username": event.username,
        "password": event.password,
        "command": event.command,
        "payload": event.payload,
        "raw_data": event.raw_data,
        "country": event.country,
        "is_attack": event.is_attack,
        "attack_type": event.attack_type,
        "severity": event.severity,
        "timestamp": event.timestamp.isoformat() if event.timestamp else None,
        "metadata": event.metadata,
    }


@router.post("/start")
def start_honeypots(
    current_user: User = Depends(get_current_user),
):
    listeners = honeypot_service.start_honeypots(SessionLocal)
    return {"status": "started", "listeners": len(listeners), "ports": list(honeypot_service.HONEYPOT_SERVICES.keys())}


@router.post("/stop")
def stop_honeypots(
    current_user: User = Depends(get_current_user),
):
    honeypot_service.stop_honeypots()
    return {"status": "stopped"}


@router.get("/status")
def honeypot_status():
    return {
        "running": honeypot_service._running,
        "active_listeners": len(honeypot_service._active_listeners),
        "services": honeypot_service.HONEYPOT_SERVICES,
    }


@router.get("/stats")
def honeypot_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from sqlalchemy import func
    total = db.query(HoneypotEvent).count()
    by_service = (
        db.query(HoneypotEvent.service, func.count(HoneypotEvent.id))
        .group_by(HoneypotEvent.service)
        .all()
    )
    by_attack = (
        db.query(HoneypotEvent.attack_type, func.count(HoneypotEvent.id))
        .group_by(HoneypotEvent.attack_type)
        .order_by(desc(func.count(HoneypotEvent.id)))
        .limit(10)
        .all()
    )
    top_ips = (
        db.query(HoneypotEvent.source_ip, func.count(HoneypotEvent.id))
        .group_by(HoneypotEvent.source_ip)
        .order_by(desc(func.count(HoneypotEvent.id)))
        .limit(10)
        .all()
    )
    return {
        "total_events": total,
        "by_service": dict(by_service),
        "by_attack_type": dict(by_attack),
        "top_attacker_ips": [{"ip": ip, "count": cnt} for ip, cnt in top_ips if ip],
    }

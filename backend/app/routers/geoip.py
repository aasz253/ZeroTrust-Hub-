from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional
from app.database.session import get_db
from app.models.geoip import GeoIPRule, GeoIPCache, GeoIPHit
from app.models.user import User
from app.core.security import get_current_user
from app.services import geoip_service
from datetime import datetime, timezone
from pydantic import BaseModel

router = APIRouter(prefix="/api/geoip", tags=["GeoIP"])


class RuleCreate(BaseModel):
    country_code: str
    country_name: str
    action: str = "block"
    notes: str = ""


@router.get("/rules")
def list_rules(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rules = db.query(GeoIPRule).order_by(GeoIPRule.created_at.desc()).all()
    return {
        "items": [
            {
                "id": r.id,
                "country_code": r.country_code,
                "country_name": r.country_name,
                "action": r.action,
                "notes": r.notes,
                "is_active": r.is_active,
                "hit_count": r.hit_count or 0,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in rules
        ]
    }


@router.post("/rules")
def create_rule(
    request: RuleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = db.query(GeoIPRule).filter(GeoIPRule.country_code == request.country_code.upper()).first()
    if existing:
        raise HTTPException(status_code=400, detail="Rule for this country already exists")

    rule = GeoIPRule(
        country_code=request.country_code.upper(),
        country_name=request.country_name,
        action=request.action,
        notes=request.notes,
        created_by=current_user.id,
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return {"id": rule.id, "country_code": rule.country_code, "action": rule.action}


@router.delete("/rules/{rule_id}")
def delete_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rule = db.query(GeoIPRule).filter(GeoIPRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    db.delete(rule)
    db.commit()
    return {"detail": "Rule deleted"}


@router.post("/rules/{rule_id}/toggle")
def toggle_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rule = db.query(GeoIPRule).filter(GeoIPRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    rule.is_active = not rule.is_active
    db.commit()
    return {"id": rule.id, "is_active": rule.is_active}


@router.get("/lookup")
def lookup_ip(
    ip: str = Query(..., description="IP address to look up"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    info = geoip_service.get_ip_info(ip, db)
    return info


@router.get("/hits")
def list_hits(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    country_code: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(GeoIPHit)
    if country_code:
        q = q.filter(GeoIPHit.country_code == country_code.upper())

    total = q.count()
    items = q.order_by(desc(GeoIPHit.timestamp)).offset((page - 1) * page_size).limit(page_size).all()
    return {
        "items": [
            {
                "id": h.id,
                "ip_address": h.ip_address,
                "country_code": h.country_code,
                "country_name": h.country_name,
                "action": h.action,
                "path": h.path,
                "user_agent": h.user_agent[:200] if h.user_agent else None,
                "timestamp": h.timestamp.isoformat() if h.timestamp else None,
            }
            for h in items
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/stats")
def geoip_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from sqlalchemy import func
    total_rules = db.query(GeoIPRule).count()
    active_rules = db.query(GeoIPRule).filter(GeoIPRule.is_active == True).count()
    total_hits = db.query(GeoIPHit).count()
    blocked_countries = (
        db.query(GeoIPRule.country_code, GeoIPRule.country_name, GeoIPRule.hit_count)
        .filter(GeoIPRule.is_active == True, GeoIPRule.action == "block")
        .order_by(GeoIPRule.hit_count.desc())
        .all()
    )
    return {
        "total_rules": total_rules,
        "active_rules": active_rules,
        "total_hits": total_hits,
        "blocked_countries": [
            {"code": c, "name": n, "hits": h or 0}
            for c, n, h in blocked_countries
        ],
    }

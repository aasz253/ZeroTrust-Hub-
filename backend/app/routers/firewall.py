from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional
from app.database.session import get_db
from app.models.firewall import FirewallRule
from app.models.user import User
from app.core.security import get_current_user
from app.services import firewall_service
from datetime import datetime, timezone
from pydantic import BaseModel

router = APIRouter(prefix="/api/firewall", tags=["Firewall"])


class RuleCreate(BaseModel):
    name: str
    description: str = ""
    action: str = "block"
    direction: str = "inbound"
    protocol: str = "any"
    source_ip: str = None
    destination_ip: str = None
    source_port: int = None
    destination_port: int = None
    interface: str = None
    priority: int = 0
    log_hits: bool = False


@router.get("/rules")
def list_rules(
    action: Optional[str] = Query(None),
    direction: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(FirewallRule)
    if action:
        q = q.filter(FirewallRule.action == action)
    if direction:
        q = q.filter(FirewallRule.direction == direction)
    if is_active is not None:
        q = q.filter(FirewallRule.is_active == is_active)

    items = q.order_by(FirewallRule.priority.asc(), desc(FirewallRule.created_at)).all()
    return {
        "items": [
            {
                "id": r.id,
                "name": r.name,
                "description": r.description,
                "action": r.action,
                "direction": r.direction,
                "protocol": r.protocol,
                "source_ip": r.source_ip,
                "destination_ip": r.destination_ip,
                "source_port": r.source_port,
                "destination_port": r.destination_port,
                "interface": r.interface,
                "priority": r.priority,
                "is_active": r.is_active,
                "is_system": r.is_system,
                "log_hits": r.log_hits,
                "hit_count": r.hit_count,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in items
        ]
    }


@router.post("/rules")
def create_rule(
    request: RuleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rule = FirewallRule(
        name=request.name,
        description=request.description,
        action=request.action,
        direction=request.direction,
        protocol=request.protocol,
        source_ip=request.source_ip,
        destination_ip=request.destination_ip,
        source_port=request.source_port,
        destination_port=request.destination_port,
        interface=request.interface,
        priority=request.priority,
        log_hits=request.log_hits,
        created_by=current_user.id,
    )
    db.add(rule)
    db.flush()

    success = firewall_service.apply_rule(rule, add=True)
    if not success:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to apply firewall rule")

    db.commit()
    db.refresh(rule)
    return {"id": rule.id, "name": rule.name, "applied": True}


@router.delete("/rules/{rule_id}")
def delete_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rule = db.query(FirewallRule).filter(FirewallRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    if rule.is_system:
        raise HTTPException(status_code=400, detail="Cannot delete system rules")

    firewall_service.apply_rule(rule, add=False)
    db.delete(rule)
    db.commit()
    return {"detail": "Rule deleted"}


@router.post("/rules/{rule_id}/toggle")
def toggle_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rule = db.query(FirewallRule).filter(FirewallRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")

    rule.is_active = not rule.is_active
    if rule.is_active:
        firewall_service.apply_rule(rule, add=True)
    else:
        firewall_service.apply_rule(rule, add=False)
    db.commit()
    return {"id": rule.id, "is_active": rule.is_active}


@router.post("/sync")
def sync_rules(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = firewall_service.sync_rules_to_system(db)
    return result


@router.get("/status")
def firewall_status():
    return {
        "firewall_type": firewall_service.get_firewall_type(),
        "system_rules": firewall_service.get_system_rules()[:20],
    }

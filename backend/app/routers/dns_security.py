from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional
from app.database.session import get_db
from app.models.dns_security import MaliciousDomain, DNSQuery, DNSBlockerRule
from app.models.user import User
from app.core.security import get_current_user
from app.services import dns_service
from pydantic import BaseModel

router = APIRouter(prefix="/api/dns", tags=["DNS Security"])


class BlockedDomainCreate(BaseModel):
    domain: str
    threat_type: str = "manual"
    confidence: float = 1.0
    source: str = "manual"


class BlockerRuleCreate(BaseModel):
    domain: str
    pattern_type: str = "exact"
    action: str = "block"
    category: str = None
    description: str = ""


@router.get("/domains")
def list_malicious_domains(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    total = db.query(MaliciousDomain).count()
    items = db.query(MaliciousDomain).order_by(desc(MaliciousDomain.last_seen)).offset((page - 1) * page_size).limit(page_size).all()
    return {
        "items": [
            {
                "id": d.id,
                "domain": d.domain,
                "threat_type": d.threat_type,
                "severity": d.severity,
                "source": d.source,
                "confidence": d.confidence,
                "is_active": d.is_active,
                "first_seen": d.first_seen.isoformat() if d.first_seen else None,
                "last_seen": d.last_seen.isoformat() if d.last_seen else None,
            }
            for d in items
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.post("/domains")
def add_malicious_domain(
    request: BlockedDomainCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = dns_service.add_malicious_domain(
        domain=request.domain,
        threat_type=request.threat_type,
        confidence=request.confidence,
        source=request.source,
        db=db,
    )
    return result


@router.post("/domains/{domain_id}/toggle")
def toggle_domain(
    domain_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    domain = db.query(MaliciousDomain).filter(MaliciousDomain.id == domain_id).first()
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    domain.is_active = not domain.is_active
    db.commit()
    return {"id": domain.id, "is_active": domain.is_active}


@router.delete("/domains/{domain_id}")
def delete_domain(
    domain_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    domain = db.query(MaliciousDomain).filter(MaliciousDomain.id == domain_id).first()
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    db.delete(domain)
    db.commit()
    return {"detail": "Domain removed"}


@router.post("/blocker-rules")
def create_blocker_rule(
    request: BlockerRuleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rule = DNSBlockerRule(
        domain=request.domain.lower(),
        pattern_type=request.pattern_type,
        action=request.action,
        category=request.category,
        description=request.description,
        created_by=current_user.id,
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return {"id": rule.id, "domain": rule.domain, "pattern_type": rule.pattern_type}


@router.get("/blocker-rules")
def list_blocker_rules(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rules = db.query(DNSBlockerRule).order_by(desc(DNSBlockerRule.created_at)).all()
    return {
        "items": [
            {
                "id": r.id,
                "domain": r.domain,
                "pattern_type": r.pattern_type,
                "action": r.action,
                "category": r.category,
                "description": r.description,
                "is_active": r.is_active,
                "hit_count": r.hit_count or 0,
            }
            for r in rules
        ]
    }


@router.delete("/blocker-rules/{rule_id}")
def delete_blocker_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rule = db.query(DNSBlockerRule).filter(DNSBlockerRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    db.delete(rule)
    db.commit()
    return {"detail": "Rule removed"}


@router.post("/check")
def check_domain(
    domain: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = dns_service.analyze_query(domain, db=db)
    return result


@router.get("/queries")
def list_queries(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    malicious_only: bool = Query(False),
    blocked_only: bool = Query(False),
    source_ip: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(DNSQuery)
    if malicious_only:
        q = q.filter(DNSQuery.is_malicious == True)
    if blocked_only:
        q = q.filter(DNSQuery.is_blocked == True)
    if source_ip:
        q = q.filter(DNSQuery.source_ip == source_ip)

    total = q.count()
    items = q.order_by(desc(DNSQuery.timestamp)).offset((page - 1) * page_size).limit(page_size).all()
    return {
        "items": [
            {
                "id": q.id,
                "timestamp": q.timestamp.isoformat() if q.timestamp else None,
                "source_ip": q.source_ip,
                "domain": q.domain,
                "query_type": q.query_type,
                "response_ip": q.response_ip,
                "is_blocked": q.is_blocked,
                "is_malicious": q.is_malicious,
                "threat_match": q.threat_match,
                "duration_ms": q.duration_ms,
            }
            for q in items
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/stats")
def dns_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from sqlalchemy import func
    total_queries = db.query(DNSQuery).count()
    blocked = db.query(DNSQuery).filter(DNSQuery.is_blocked == True).count()
    malicious = db.query(DNSQuery).filter(DNSQuery.is_malicious == True).count()
    domains = db.query(MaliciousDomain).count()
    rules = db.query(DNSBlockerRule).filter(DNSBlockerRule.is_active == True).count()
    return {
        "total_queries": total_queries,
        "blocked": blocked,
        "malicious": malicious,
        "malicious_domains": domains,
        "active_rules": rules,
    }

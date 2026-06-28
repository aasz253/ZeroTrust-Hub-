from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional
from app.database.session import get_db
from app.models.vuln_prioritization import VulnPriority
from app.models.user import User
from app.core.security import get_current_user
from app.services import vuln_prioritization_service

router = APIRouter(prefix="/api/vuln-priority", tags=["Vulnerability Prioritization"])


@router.get("/scored")
def list_scored(
    priority_tier: Optional[str] = Query(None),
    cisa_kev_only: bool = Query(False),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(VulnPriority)
    if priority_tier:
        q = q.filter(VulnPriority.priority_tier == priority_tier.upper())
    if cisa_kev_only:
        q = q.filter(VulnPriority.is_cisa_kev == True)
    if search:
        q = q.filter(VulnPriority.cve_id.ilike(f"%{search}%"))

    total = q.count()
    items = q.order_by(desc(VulnPriority.combined_score)).offset((page - 1) * page_size).limit(page_size).all()
    return {
        "items": [
            {
                "id": v.id,
                "cve_id": v.cve_id,
                "cvss_score": v.cvss_score,
                "cvss_severity": v.cvss_severity,
                "epss_score": v.epss_score,
                "epss_percentile": v.epss_percentile,
                "is_cisa_kev": v.is_cisa_kev,
                "combined_score": v.combined_score,
                "priority_tier": v.priority_tier,
                "affected_vendor": v.affected_vendor,
                "affected_product": v.affected_product,
                "description": v.description,
                "last_updated": v.last_updated.isoformat() if v.last_updated else None,
            }
            for v in items
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/scored/{cve_id}")
def get_scored(
    cve_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    entry = db.query(VulnPriority).filter(VulnPriority.cve_id == cve_id.upper()).first()
    if not entry:
        raise HTTPException(status_code=404, detail="CVE not found in prioritization database")
    return {
        "id": entry.id,
        "cve_id": entry.cve_id,
        "cvss_score": entry.cvss_score,
        "epss_score": entry.epss_score,
        "epss_percentile": entry.epss_percentile,
        "is_cisa_kev": entry.is_cisa_kev,
        "combined_score": entry.combined_score,
        "priority_tier": entry.priority_tier,
        "affected_vendor": entry.affected_vendor,
        "affected_product": entry.affected_product,
        "description": entry.description,
    }


@router.post("/score/{cve_id}")
def score_cve(
    cve_id: str,
    cvss_score: float = Query(0.0),
    affected_vendor: str = Query(""),
    affected_product: str = Query(""),
    description: str = Query(""),
    is_kev: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = vuln_prioritization_service.prioritize_cve(
        cve_id=cve_id.upper(),
        cvss_score=cvss_score,
        affected_vendor=affected_vendor,
        affected_product=affected_product,
        description=description,
        is_kev=is_kev,
        db=db,
    )
    return result


@router.post("/batch-score")
def batch_score(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = vuln_prioritization_service.batch_prioritize(db)
    return result


@router.get("/stats")
def priority_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from sqlalchemy import func
    total = db.query(VulnPriority).count()
    critical = db.query(VulnPriority).filter(VulnPriority.priority_tier == "CRITICAL").count()
    high = db.query(VulnPriority).filter(VulnPriority.priority_tier == "HIGH").count()
    medium = db.query(VulnPriority).filter(VulnPriority.priority_tier == "MEDIUM").count()
    low = db.query(VulnPriority).filter(VulnPriority.priority_tier == "LOW").count()
    cisa_kev = db.query(VulnPriority).filter(VulnPriority.is_cisa_kev == True).count()
    avg_combined = db.query(func.avg(VulnPriority.combined_score)).scalar() or 0
    return {
        "total": total,
        "critical": critical,
        "high": high,
        "medium": medium,
        "low": low,
        "cisa_kev": cisa_kev,
        "avg_combined_score": round(float(avg_combined), 2),
    }

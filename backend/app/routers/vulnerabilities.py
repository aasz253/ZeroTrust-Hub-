from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database.session import get_db
from app.services.vulnerability_service import VulnerabilityService
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.scan import VulnerabilityResponse

router = APIRouter(prefix="/api/cves", tags=["Vulnerabilities"])


@router.get("")
def search_cves(
    query: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    vendor: Optional[str] = Query(None),
    product: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = VulnerabilityService(db)
    return service.search_cves(query, severity, vendor, product, page, page_size)


@router.get("/{cve_id}")
def get_cve(
    cve_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from sqlalchemy.orm import Session
    from app.models.vulnerability import Vulnerability

    vuln = db.query(Vulnerability).filter(Vulnerability.cve_id == cve_id).first()
    if not vuln:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CVE not found",
        )
    return vuln


@router.post("/sync")
async def sync_cves(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role.name != "admin":
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    service = VulnerabilityService(db)
    results = await service.fetch_from_nvd()
    count = 0
    for vuln in results:
        existing = (
            db.query(type(vuln))
            .filter(type(vuln).cve_id == vuln.cve_id)
            .first()
        )
        if not existing:
            db.add(vuln)
            count += 1
    db.commit()
    return {"detail": f"Synced {count} new vulnerabilities"}

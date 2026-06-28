from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional
from app.database.session import get_db
from app.models.ssl_monitor import SSLCertificate
from app.models.user import User
from app.core.security import get_current_user
from app.services import ssl_monitor_service
from pydantic import BaseModel

router = APIRouter(prefix="/api/ssl", tags=["SSL/TLS Monitor"])


class DomainAdd(BaseModel):
    domain: str
    port: int = None


@router.get("/certificates")
def list_certificates(
    status_filter: Optional[str] = Query(None, alias="status"),
    expiring_only: bool = Query(False),
    expired_only: bool = Query(False),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(SSLCertificate)
    if status_filter:
        q = q.filter(SSLCertificate.status == status_filter)
    if expiring_only:
        q = q.filter(SSLCertificate.is_expiring_soon == True)
    if expired_only:
        q = q.filter(SSLCertificate.is_expired == True)
    if search:
        q = q.filter(SSLCertificate.domain.ilike(f"%{search}%"))

    total = q.count()
    items = q.order_by(SSLCertificate.days_remaining.asc()).offset((page - 1) * page_size).limit(page_size).all()
    return {
        "items": [
            {
                "id": c.id,
                "domain": c.domain,
                "port": c.port,
                "issuer": c.issuer,
                "subject": c.subject,
                "valid_from": c.valid_from.isoformat() if c.valid_from else None,
                "valid_to": c.valid_to.isoformat() if c.valid_to else None,
                "days_remaining": c.days_remaining or 0,
                "is_expired": c.is_expired,
                "is_expiring_soon": c.is_expiring_soon,
                "is_self_signed": c.is_self_signed,
                "is_wildcard": c.is_wildcard,
                "weak_cipher": c.weak_cipher,
                "protocol_version": c.protocol_version,
                "cipher_suite": c.cipher_suite,
                "status": c.status,
                "dns_names": c.dns_names or [],
                "last_checked": c.last_checked.isoformat() if c.last_checked else None,
            }
            for c in items
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.post("/scan")
def scan_domain(
    request: DomainAdd,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = ssl_monitor_service.scan_domain(request.domain, request.port, db)
    return result


@router.post("/scan-all")
def scan_all_domains(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    certs = db.query(SSLCertificate).all()
    results = []
    for cert in certs:
        result = ssl_monitor_service.scan_domain(cert.domain, cert.port, db)
        results.append({"domain": cert.domain, "status": result.get("status")})
    return {"scanned": len(results), "results": results}


@router.delete("/certificates/{cert_id}")
def delete_certificate(
    cert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cert = db.query(SSLCertificate).filter(SSLCertificate.id == cert_id).first()
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found")
    db.delete(cert)
    db.commit()
    return {"detail": "Certificate removed"}


@router.get("/stats")
def ssl_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from sqlalchemy import func
    total = db.query(SSLCertificate).count()
    expired = db.query(SSLCertificate).filter(SSLCertificate.is_expired == True).count()
    expiring = db.query(SSLCertificate).filter(SSLCertificate.is_expiring_soon == True).count()
    weak = db.query(SSLCertificate).filter(SSLCertificate.weak_cipher == True).count()
    valid = db.query(SSLCertificate).filter(SSLCertificate.status == "valid").count()
    return {
        "total": total,
        "expired": expired,
        "expiring_soon": expiring,
        "weak_ciphers": weak,
        "valid": valid,
    }

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database.session import get_db
from app.models.scan import Scan
from app.models.user import User
from app.core.security import get_current_user
from app.schemas.scan import ScanCreate, ScanResponse
from datetime import datetime, timezone

router = APIRouter(prefix="/api/scans", tags=["Scans"])


@router.post("", response_model=ScanResponse)
def create_scan(
    request: ScanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    scan = Scan(
        user_id=current_user.id,
        target=request.target,
        scan_type=request.scan_type,
        status="pending",
        created_at=datetime.now(timezone.utc),
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)
    return scan


@router.get("")
def list_scans(
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(Scan).filter(Scan.user_id == current_user.id)
    total = q.count()
    items = (
        q.order_by(desc(Scan.created_at))
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return {
        "items": [ScanResponse.model_validate(s) for s in items],
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size,
    }


@router.get("/{scan_id}", response_model=ScanResponse)
def get_scan(
    scan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    scan = (
        db.query(Scan)
        .filter(Scan.id == scan_id, Scan.user_id == current_user.id)
        .first()
    )
    if not scan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scan not found")
    return scan

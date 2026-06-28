from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database.session import get_db
from app.models.scan import Scan
from app.models.user import User
from app.core.security import get_current_user
from app.schemas.scan import ScanCreate, ScanResponse
from app.services.scan_service import quick_scan, full_scan, port_scan
from datetime import datetime, timezone
import threading

router = APIRouter(prefix="/api/scans", tags=["Scans"])


def run_scan_background(scan_id: int, target: str, scan_type: str):
    from app.database.session import SessionLocal
    db = SessionLocal()
    try:
        scan = db.query(Scan).filter(Scan.id == scan_id).first()
        if not scan:
            return

        scan.status = "running"
        scan.started_at = datetime.now(timezone.utc)
        db.commit()

        if scan_type == "quick":
            result = quick_scan(target)
        elif scan_type == "full":
            result = full_scan(target)
        elif scan_type == "port":
            result = port_scan(target)
        else:
            result = quick_scan(target)

        if "error" in result:
            scan.status = "failed"
            scan.result_summary = result
            db.commit()
            return

        summary = result.get("summary", result)
        scan.status = "completed"
        scan.progress = 100
        scan.findings_count = summary.get("total", 0)
        scan.critical_count = summary.get("critical", 0)
        scan.high_count = summary.get("high", 0)
        scan.medium_count = summary.get("medium", 0)
        scan.low_count = summary.get("low", 0)
        scan.result_summary = result
        scan.completed_at = datetime.now(timezone.utc)

        if scan.critical_count > 0:
            scan.severity = "CRITICAL"
        elif scan.high_count > 0:
            scan.severity = "HIGH"
        elif scan.medium_count > 0:
            scan.severity = "MEDIUM"
        else:
            scan.severity = "LOW"

        db.commit()
    except Exception as e:
        if scan := db.query(Scan).filter(Scan.id == scan_id).first():
            scan.status = "failed"
            scan.result_summary = {"error": str(e)}
            db.commit()
    finally:
        db.close()


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
        progress=0,
        created_at=datetime.now(timezone.utc),
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)

    thread = threading.Thread(
        target=run_scan_background,
        args=(scan.id, request.target, request.scan_type),
        daemon=True,
    )
    thread.start()

    return scan


@router.get("")
def list_scans(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
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

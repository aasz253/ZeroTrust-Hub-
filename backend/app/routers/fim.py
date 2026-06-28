from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional
from app.database.session import get_db
from app.models.user import User
from app.models.fim import FimEntry
from app.core.security import get_current_user
from app.services import fim_service
from pydantic import BaseModel

router = APIRouter(prefix="/api/fim", tags=["FIM"])


class AddPathRequest(BaseModel):
    file_path: str


@router.get("/entries")
def list_entries(
    status_filter: Optional[str] = Query(None),
    critical_only: bool = Query(False),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(FimEntry)
    if status_filter:
        q = q.filter(FimEntry.status == status_filter)
    if critical_only:
        q = q.filter(FimEntry.is_critical == True)

    total = q.count()
    items = q.order_by(desc(FimEntry.last_changed)).offset((page - 1) * page_size).limit(page_size).all()
    pages = max(1, (total + page_size - 1) // page_size)

    return {
        "items": [
            {
                "id": e.id,
                "file_path": e.file_path,
                "file_name": e.file_name,
                "status": e.status,
                "current_hash": e.current_hash,
                "previous_hash": e.previous_hash,
                "file_size": e.file_size,
                "permissions": e.permissions,
                "owner": e.owner,
                "last_checked": e.last_checked.isoformat() if e.last_checked else None,
                "last_changed": e.last_changed.isoformat() if e.last_changed else None,
                "change_count": e.change_count or 0,
                "is_critical": e.is_critical,
            }
            for e in items
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": pages,
    }


@router.post("/scan")
def scan_files(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    results = fim_service.scan_all_watched(db)
    changed = sum(1 for r in results if r["status"] == "changed")
    return {
        "scanned": len(results),
        "changed": changed,
        "results": results,
    }


@router.post("/add")
def add_path(
    request: AddPathRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = fim_service.add_watched_path(db, request.file_path)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error", "Failed to add path"))
    return result


@router.get("/stats")
def fim_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from sqlalchemy import func
    total = db.query(FimEntry).count()
    changed = db.query(FimEntry).filter(FimEntry.status == "changed").count()
    critical = db.query(FimEntry).filter(FimEntry.is_critical == True).count()
    monitored = db.query(FimEntry).filter(FimEntry.status == "monitored").count()
    return {
        "total_files": total,
        "changed": changed,
        "critical": critical,
        "monitored": monitored,
    }

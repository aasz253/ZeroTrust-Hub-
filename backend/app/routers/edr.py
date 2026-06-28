from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from app.database.session import get_db
from app.models.user import User
from app.core.security import get_current_user
from app.services import edr_service

router = APIRouter(prefix="/api/edr", tags=["EDR"])


@router.get("/processes")
def list_processes(
    suspicious_only: bool = Query(False),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
):
    processes = edr_service.scan_processes()

    if suspicious_only:
        processes = [p for p in processes if p["is_suspicious"]]

    if search:
        q = search.lower()
        processes = [p for p in processes if q in (p["name"] or "").lower() or q in (p["cmdline"] or "").lower()]

    total = len(processes)
    return {
        "items": processes[:100],
        "total": total,
        "suspicious_count": sum(1 for p in processes if p["is_suspicious"]),
    }


@router.get("/processes/{pid}")
def get_process(
    pid: int,
    current_user: User = Depends(get_current_user),
):
    detail = edr_service.get_process_detail(pid)
    if not detail:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Process not found")
    return detail


@router.get("/stats")
def edr_stats(
    current_user: User = Depends(get_current_user),
):
    processes = edr_service.scan_processes()
    return {
        "total_processes": len(processes),
        "suspicious_count": sum(1 for p in processes if p["is_suspicious"]),
        "high_cpu_count": sum(1 for p in processes if p["cpu_percent"] > 50),
        "high_memory_count": sum(1 for p in processes if p["memory_percent"] > 20),
    }

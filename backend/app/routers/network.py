from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from app.database.session import get_db
from app.models.network import Device
from app.models.user import User
from app.core.security import get_current_user
from app.schemas.network import DeviceResponse, NetworkStats

router = APIRouter(prefix="/api/network", tags=["Network"])


@router.get("/devices")
def list_devices(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(Device)
    if status:
        q = q.filter(Device.status == status)

    total = q.count()
    items = q.order_by(Device.last_seen.desc()).offset((page - 1) * page_size).limit(page_size).all()
    pages = max(1, (total + page_size - 1) // page_size)

    return {
        "items": [DeviceResponse.model_validate(d) for d in items],
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": pages,
    }


@router.get("/stats")
def network_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    total = db.query(Device).count()
    online = db.query(Device).filter(Device.status == "online").count()
    offline = db.query(Device).filter(Device.status == "offline").count()
    suspicious = db.query(Device).filter(Device.status == "suspicious").count()

    ports_total = db.query(func.sum(
        func.json_array_length(Device.open_ports)
    )).scalar() or 0

    risk_avg = db.query(func.avg(Device.risk_score)).scalar() or 0.0

    return NetworkStats(
        total_devices=total,
        online_count=online,
        offline_count=offline,
        suspicious_count=suspicious,
        open_ports_total=ports_total,
        risk_score_avg=round(float(risk_avg), 2),
    )

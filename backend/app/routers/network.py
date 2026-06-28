from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database.session import get_db
from app.models.user import User
from app.core.security import get_current_user
from app.services.network_service import discover_devices, get_network_info

router = APIRouter(prefix="/api/network", tags=["Network"])


@router.get("/devices")
def list_devices(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    status: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
):
    all_devices = discover_devices()

    if status:
        all_devices = [d for d in all_devices if d["status"] == status]

    total = len(all_devices)
    start = (page - 1) * page_size
    items = all_devices[start:start + page_size]
    pages = max(1, (total + page_size - 1) // page_size)

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": pages,
    }


@router.get("/info")
def network_info(
    current_user: User = Depends(get_current_user),
):
    net_info = get_network_info()
    devices = discover_devices()
    online = sum(1 for d in devices if d["status"] == "online")
    offline = sum(1 for d in devices if d["status"] == "offline")
    suspicious = sum(1 for d in devices if d.get("risk_score", 0) >= 5)
    total_ports = sum(len(d["open_ports"]) for d in devices)
    avg_risk = round(
        sum(d.get("risk_score", 0) for d in devices) / (len(devices) or 1), 2
    )

    return {
        "total_devices": len(devices),
        "online_count": online,
        "offline_count": offline,
        "suspicious_count": suspicious,
        "open_ports_total": total_ports,
        "risk_score_avg": avg_risk,
        "wifi_ssid": net_info["wifi_ssid"],
        "gateway_ip": net_info["gateway_ip"],
        "interface_name": net_info["interface_name"],
    }

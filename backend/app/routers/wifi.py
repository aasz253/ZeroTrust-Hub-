from fastapi import APIRouter, Depends, HTTPException, status
from app.models.user import User
from app.core.security import get_current_user
from app.services import wifi_service
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/api/wifi", tags=["WiFi"])


class ConnectRequest(BaseModel):
    ssid: str
    password: Optional[str] = ""


@router.get("/scan")
def scan_wifi(current_user: User = Depends(get_current_user)):
    networks = wifi_service.list_available()
    return {
        "networks": networks,
        "total": len(networks),
        "active_connection": wifi_service.get_active_connection(),
    }


@router.get("/status")
def wifi_status(current_user: User = Depends(get_current_user)):
    return wifi_service.get_status()


@router.post("/connect")
def connect_wifi(
    request: ConnectRequest,
    current_user: User = Depends(get_current_user),
):
    if current_user.role.name != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can connect to WiFi networks",
        )
    result = wifi_service.connect(request.ssid, request.password)
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error", "Connection failed"),
        )
    return result


@router.post("/disconnect")
def disconnect_wifi(current_user: User = Depends(get_current_user)):
    if current_user.role.name != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can disconnect WiFi",
        )
    result = wifi_service.disconnect()
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error", "Disconnect failed"),
        )
    return result

from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.setting import Setting
from app.models.user import User
from app.core.security import get_current_admin, get_current_user
from typing import Optional

router = APIRouter(prefix="/api/settings", tags=["Settings"])


@router.get("")
def get_settings(
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    q = db.query(Setting)
    if category:
        q = q.filter(Setting.category == category)
    settings_list = q.all()
    return {
        s.key: {
            "value": s.value,
            "type": s.value_type,
            "category": s.category,
            "description": s.description,
        }
        for s in settings_list
    }


@router.put("/{key}")
def update_setting(
    key: str,
    value: str = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    setting = db.query(Setting).filter(Setting.key == key).first()
    if not setting:
        setting = Setting(key=key, value=value)
        db.add(setting)
    else:
        setting.value = value
    db.commit()
    return {"detail": "Setting updated"}

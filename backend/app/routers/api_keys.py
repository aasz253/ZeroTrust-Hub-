from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.api_key import ApiKey
from app.models.user import User
from app.core.security import get_current_admin
import secrets
import hashlib

router = APIRouter(prefix="/api/api-keys", tags=["API Keys"])


@router.get("")
def list_api_keys(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    keys = db.query(ApiKey).all()
    return [
        {
            "id": k.id,
            "name": k.name,
            "key_prefix": k.key_prefix,
            "is_active": k.is_active,
            "last_used_at": k.last_used_at.isoformat() if k.last_used_at else None,
            "created_at": k.created_at.isoformat() if k.created_at else None,
        }
        for k in keys
    ]


@router.post("")
def create_api_key(
    name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    raw_key = f"zt_{secrets.token_hex(32)}"
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
    key_prefix = raw_key[:10]

    api_key = ApiKey(
        user_id=current_user.id,
        name=name,
        key_hash=key_hash,
        key_prefix=key_prefix,
    )
    db.add(api_key)
    db.commit()

    return {
        "id": api_key.id,
        "name": api_key.name,
        "key": raw_key,
        "key_prefix": key_prefix,
    }


@router.delete("/{key_id}")
def delete_api_key(
    key_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    key = db.query(ApiKey).filter(ApiKey.id == key_id).first()
    if not key:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="API key not found")
    db.delete(key)
    db.commit()
    return {"detail": "API key deleted"}

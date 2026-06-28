from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.user import User
from app.core.security import get_current_user
from app.services import mfa_service
from pydantic import BaseModel

router = APIRouter(prefix="/api/auth/mfa", tags=["MFA"])


class SetupResponse(BaseModel):
    secret: str
    qr_code: str
    recovery_codes: list[str]


class VerifyRequest(BaseModel):
    code: str


class SetupVerifyRequest(BaseModel):
    code: str


@router.post("/setup")
def setup_mfa(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    secret = mfa_service.generate_totp_secret()
    uri = mfa_service.get_totp_uri(secret, current_user.email)
    codes = mfa_service.generate_recovery_codes(8)
    hashed_codes = mfa_service.hash_recovery_codes(codes)

    current_user.mfa_secret = secret
    current_user.mfa_recovery_codes = hashed_codes
    current_user.is_mfa_enabled = False
    db.commit()

    return {
        "secret": secret,
        "uri": uri,
        "recovery_codes": codes,
    }


@router.post("/verify-setup")
def verify_setup(
    request: SetupVerifyRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not current_user.mfa_secret:
        raise HTTPException(status_code=400, detail="MFA not set up")

    if mfa_service.verify_totp(current_user.mfa_secret, request.code):
        current_user.is_mfa_enabled = True
        db.commit()
        return {"detail": "MFA enabled successfully"}
    raise HTTPException(status_code=400, detail="Invalid code")


@router.post("/verify")
def verify_mfa(
    request: VerifyRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not current_user.is_mfa_enabled or not current_user.mfa_secret:
        raise HTTPException(status_code=400, detail="MFA not enabled")

    if mfa_service.verify_totp(current_user.mfa_secret, request.code):
        return {"detail": "Code verified"}

    codes = current_user.mfa_recovery_codes or []
    if mfa_service.verify_recovery_code(request.code, codes):
        current_user.mfa_recovery_codes = mfa_service.remove_used_code(request.code, codes)
        db.commit()
        return {"detail": "Recovery code accepted"}

    raise HTTPException(status_code=400, detail="Invalid code")


@router.post("/disable")
def disable_mfa(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    current_user.is_mfa_enabled = False
    current_user.mfa_secret = None
    current_user.mfa_recovery_codes = None
    db.commit()
    return {"detail": "MFA disabled"}


@router.get("/status")
def mfa_status(
    current_user: User = Depends(get_current_user),
):
    return {
        "enabled": current_user.is_mfa_enabled,
        "has_secret": current_user.mfa_secret is not None,
    }

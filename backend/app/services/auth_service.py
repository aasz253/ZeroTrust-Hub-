from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Request
from app.models.user import User
from app.models.role import Role
from app.models.audit_log import AuditLog
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.services.security_service import (
    check_brute_force, record_failed_login, sanitize_input, get_client_ip,
)
from datetime import datetime, timezone


class AuthService:
    def __init__(self, db: Session, request: Request = None):
        self.db = db
        self.request = request

    def login(self, email: str, password: str) -> dict:
        ip = get_client_ip(self.request) if self.request else "unknown"

        block_reason = check_brute_force(ip, email)
        if block_reason:
            self._log_audit(0, "login_blocked", "auth", ip, block_reason)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=block_reason,
            )

        user = self.db.query(User).filter(User.email == email).first()
        if not user or not verify_password(password, user.hashed_password):
            record_failed_login(ip, email)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive",
            )

        user.last_login = datetime.now(timezone.utc)
        self.db.commit()

        self._log_audit(user.id, "login", "auth", str(user.id), "User logged in")

        return {
            "access_token": create_access_token({"sub": str(user.id)}),
            "refresh_token": create_refresh_token({"sub": str(user.id)}),
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name,
                "role": user.role.name,
            },
        }

    def register(self, email: str, username: str, password: str, full_name: str = None) -> dict:
        email = sanitize_input(email.strip().lower())
        username = sanitize_input(username.strip())
        full_name = sanitize_input(full_name.strip()) if full_name else None

        if len(password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters",
            )

        existing = self.db.query(User).filter(
            (User.email == email) | (User.username == username)
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email or username already exists",
            )

        default_role = self.db.query(Role).filter(Role.name == "analyst").first()
        if not default_role:
            default_role = Role(name="analyst", description="Default analyst role")
            self.db.add(default_role)
            self.db.commit()
            self.db.refresh(default_role)

        user = User(
            email=email,
            username=username,
            hashed_password=hash_password(password),
            full_name=full_name,
            role_id=default_role.id,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        self._log_audit(user.id, "register", "auth", str(user.id), "User registered")

        return {
            "access_token": create_access_token({"sub": str(user.id)}),
            "refresh_token": create_refresh_token({"sub": str(user.id)}),
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name,
                "role": user.role.name,
            },
        }

    def refresh_token(self, refresh_token: str) -> dict:
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )
        user_id = payload.get("sub")
        user = self.db.query(User).filter(User.id == int(user_id)).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
            )
        return {
            "access_token": create_access_token({"sub": str(user.id)}),
            "refresh_token": create_refresh_token({"sub": str(user.id)}),
            "token_type": "bearer",
        }

    def _log_audit(self, user_id: int, action: str, resource: str, resource_id: str, details: str):
        log = AuditLog(
            user_id=user_id,
            action=action,
            resource=resource,
            resource_id=resource_id,
            details=details,
        )
        self.db.add(log)
        self.db.commit()

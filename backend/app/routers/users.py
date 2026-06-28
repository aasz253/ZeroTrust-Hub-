from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database.session import get_db
from app.models.user import User
from app.models.role import Role, Permission
from app.core.security import get_current_admin, get_current_user, hash_password
from app.schemas.user import UserUpdate, UserAdminResponse, RoleCreate, PermissionResponse

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.get("")
def list_users(
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    total = db.query(User).count()
    users = (
        db.query(User)
        .order_by(desc(User.created_at))
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return {
        "items": [
            UserAdminResponse(
                id=u.id,
                email=u.email,
                username=u.username,
                full_name=u.full_name,
                is_active=u.is_active,
                is_mfa_enabled=u.is_mfa_enabled,
                role=u.role.name if u.role else "unknown",
                last_login=u.last_login,
                created_at=u.created_at,
            )
            for u in users
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size,
    }


@router.get("/{user_id}")
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserAdminResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        is_active=user.is_active,
        is_mfa_enabled=user.is_mfa_enabled,
        role=user.role.name if user.role else "unknown",
        last_login=user.last_login,
        created_at=user.created_at,
    )


@router.patch("/{user_id}")
def update_user(
    user_id: int,
    request: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    for key, value in request.model_dump(exclude_none=True).items():
        setattr(user, key, value)
    db.commit()
    return {"detail": "User updated"}


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user.id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete yourself")
    db.delete(user)
    db.commit()
    return {"detail": "User deleted"}


@router.get("/roles/list")
def list_roles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    roles = db.query(Role).all()
    return [
        {
            "id": r.id,
            "name": r.name,
            "description": r.description,
            "permissions": [p.name for p in r.permissions],
        }
        for r in roles
    ]


@router.get("/permissions")
def list_permissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    permissions = db.query(Permission).all()
    return [PermissionResponse.model_validate(p) for p in permissions]

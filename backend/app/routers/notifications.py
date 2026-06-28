from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database.session import get_db
from app.models.notification import Notification
from app.models.user import User
from app.core.security import get_current_user
from app.schemas.notification import NotificationResponse, NotificationUpdate
from typing import Optional

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])


@router.get("")
def list_notifications(
    is_read: Optional[bool] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(Notification).filter(Notification.user_id == current_user.id)
    if is_read is not None:
        q = q.filter(Notification.is_read == is_read)
    total = q.count()
    items = (
        q.order_by(desc(Notification.created_at))
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return {
        "items": [NotificationResponse.model_validate(n) for n in items],
        "total": total,
        "unread": db.query(Notification)
        .filter(Notification.user_id == current_user.id, Notification.is_read == False)
        .count(),
        "page": page,
        "page_size": page_size,
    }


@router.patch("/{notification_id}")
def update_notification(
    notification_id: int,
    request: NotificationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    notification = (
        db.query(Notification)
        .filter(
            Notification.id == notification_id,
            Notification.user_id == current_user.id,
        )
        .first()
    )
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found"
        )
    notification.is_read = request.is_read
    db.commit()
    return {"detail": "Notification updated"}


@router.post("/mark-all-read")
def mark_all_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db.query(Notification).filter(
        Notification.user_id == current_user.id, Notification.is_read == False
    ).update({"is_read": True})
    db.commit()
    return {"detail": "All notifications marked as read"}

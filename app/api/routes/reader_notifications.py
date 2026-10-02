from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.notification import NotificationResponse
from app.services.notifications import (
    delete_notification,
    get_notification,
    list_notifications,
    mark_notification_as_read,
)


router = APIRouter(
    prefix="/v1/reader/notifications",
    tags=["Reader Notifications"],
)


@router.get(
    "",
    response_model=list[NotificationResponse],
)
def get_reader_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return list_notifications(
        db=db,
        user_id=current_user.id,
    )


@router.get(
    "/{notification_id}",
    response_model=NotificationResponse,
)
def get_reader_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    notification = get_notification(
        db=db,
        notification_id=notification_id,
    )

    if notification is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )

    if notification.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )

    return notification


@router.put(
    "/{notification_id}/read",
    response_model=NotificationResponse,
)
def mark_reader_notification_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    notification = mark_notification_as_read(
        db=db,
        notification_id=notification_id,
        user_id=current_user.id,
    )

    if notification is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )

    return notification


@router.delete(
    "/{notification_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_reader_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    deleted = delete_notification(
        db=db,
        notification_id=notification_id,
        user_id=current_user.id,
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )

    return None
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import (
    get_current_user,
    get_db,
    require_permission,
)
from app.models.user import User
from app.schemas.notification import (
    NotificationCreate,
    NotificationResponse,
)
from app.services.notifications import (
    create_notification,
    delete_notification,
    get_notification,
    list_notifications,
    mark_notification_as_read,
)


router = APIRouter(
    prefix="/v1/notifications",
    tags=["Notifications"],
)


@router.get(
    "",
    response_model=list[NotificationResponse],
)
def get_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("notifications.read")
    ),
):
    return list_notifications(
        db=db,
        user_id=current_user.id,
    )


@router.get(
    "/{notification_id}",
    response_model=NotificationResponse,
)
def get_notification_by_id(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("notifications.read")
    ),
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
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot access this notification",
        )

    return notification


@router.post(
    "",
    response_model=NotificationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_notification_endpoint(
    data: NotificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("notifications.manage")
    ),
):
    try:
        return create_notification(
            db=db,
            user_id=data.user_id,
            notification_type=data.notification_type,
            title=data.title,
            message=data.message,
            data=data.data,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.put(
    "/{notification_id}/read",
    response_model=NotificationResponse,
)
def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("notifications.manage")
    ),
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
def delete_notification_endpoint(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("notifications.manage")
    ),
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
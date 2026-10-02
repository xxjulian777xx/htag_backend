from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.notification import Notification
from app.models.user import User


def get_notification(
    db: Session,
    notification_id: int,
) -> Notification | None:

    stmt = select(Notification).where(
        Notification.id == notification_id
    )

    return db.execute(stmt).scalar_one_or_none()


def list_notifications(
    db: Session,
    *,
    user_id: int,
) -> list[Notification]:

    stmt = (
        select(Notification)
        .where(Notification.user_id == user_id)
        .order_by(Notification.created_at.desc())
    )

    return db.execute(stmt).scalars().all()


def create_notification(
    db: Session,
    *,
    user_id: int,
    notification_type: str,
    title: str,
    message: str,
    data: dict | None = None,
) -> Notification:

    user = db.get(User, user_id)

    if user is None:
        raise ValueError("User not found")

    if not user.is_active:
        raise ValueError("User is inactive")

    notification = Notification(
        user_id=user_id,
        notification_type=notification_type,
        title=title,
        message=message,
        data=data,
    )

    db.add(notification)
    db.commit()
    db.refresh(notification)

    return notification


def mark_notification_as_read(
    db: Session,
    *,
    notification_id: int,
    user_id: int,
) -> Notification | None:

    notification = get_notification(
        db=db,
        notification_id=notification_id,
    )

    if notification is None:
        return None

    if notification.user_id != user_id:
        return None

    if not notification.is_read:
        notification.is_read = True
        notification.read_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(notification)

    return notification


def delete_notification(
    db: Session,
    *,
    notification_id: int,
    user_id: int,
) -> bool:

    notification = get_notification(
        db=db,
        notification_id=notification_id,
    )

    if notification is None:
        return False

    if notification.user_id != user_id:
        return False

    db.delete(notification)
    db.commit()

    return True
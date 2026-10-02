from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.notification_event import NotificationEvent


PROCESSING_TIMEOUT_MINUTES = 10


def create_notification_event(
    db: Session,
    *,
    article_id: int,
) -> NotificationEvent:
    existing = db.execute(
        select(NotificationEvent).where(
            NotificationEvent.article_id == article_id
        )
    ).scalar_one_or_none()

    if existing is not None:
        return existing

    event = NotificationEvent(
        article_id=article_id,
        status="pending",
        attempts=0,
    )

    db.add(event)
    db.flush()

    return event


def recover_stuck_notification_events(
    db: Session,
    *,
    timeout_minutes: int = PROCESSING_TIMEOUT_MINUTES,
) -> int:
    cutoff = datetime.now(timezone.utc) - timedelta(
        minutes=timeout_minutes
    )

    stmt = (
        select(NotificationEvent)
        .where(
            NotificationEvent.status == "processing",
            NotificationEvent.updated_at < cutoff,
        )
    )

    events = db.execute(stmt).scalars().all()

    recovered = 0

    for event in events:
        event.status = "failed"
        event.last_error = (
            "Evento recuperado después de quedar "
            "en estado processing durante demasiado tiempo."
        )
        recovered += 1

    if recovered:
        db.flush()

    return recovered


def get_pending_notification_events(
    db: Session,
    *,
    limit: int = 50,
) -> list[NotificationEvent]:
    stmt = (
        select(NotificationEvent)
        .where(
            NotificationEvent.status.in_(
                ["pending", "failed"]
            )
        )
        .order_by(
            NotificationEvent.created_at.asc()
        )
        .limit(limit)
        .with_for_update(
            skip_locked=True
        )
    )

    return db.execute(stmt).scalars().all()


def mark_event_processing(
    db: Session,
    event: NotificationEvent,
) -> None:
    event.status = "processing"
    event.attempts += 1
    event.last_error = None

    db.flush()


def mark_event_sent(
    db: Session,
    event: NotificationEvent,
) -> None:
    event.status = "sent"
    event.processed_at = datetime.now(timezone.utc)
    event.last_error = None

    db.flush()


def mark_event_failed(
    db: Session,
    event: NotificationEvent,
    error: str,
) -> None:
    event.status = "failed"
    event.last_error = error

    db.flush()
import logging
import os
import time

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.article import Article
from app.models.fcm_device import FCMDevice
from app.services.fcm import send_to_tokens
from app.services.notification_events import (
    get_pending_notification_events,
    mark_event_failed,
    mark_event_processing,
    mark_event_sent,
    recover_stuck_notification_events,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [NOTIFICATION WORKER] %(levelname)s: %(message)s",
)

logger = logging.getLogger(__name__)

WORKER_INTERVAL = int(
    os.getenv("NOTIFICATION_WORKER_INTERVAL", "30")
)

BATCH_SIZE = int(
    os.getenv("NOTIFICATION_WORKER_BATCH_SIZE", "50")
)


def process_notification_event(
    db: Session,
    event,
) -> bool:
    article = db.get(
        Article,
        event.article_id,
    )

    if article is None:
        mark_event_failed(
            db=db,
            event=event,
            error="Artículo no encontrado",
        )

        db.commit()

        return False

    devices = (
        db.query(FCMDevice)
        .filter(
            FCMDevice.is_active.is_(True)
        )
        .all()
    )

    tokens = [
        device.fcm_token
        for device in devices
        if device.fcm_token
    ]

    if not tokens:
        logger.info(
            "No hay dispositivos FCM activos para el artículo %s.",
            article.id,
        )

        mark_event_sent(
            db=db,
            event=event,
        )

        db.commit()

        return True

    mark_event_processing(
        db=db,
        event=event,
    )

    db.commit()

    try:
        response = send_to_tokens(
            tokens=tokens,
            title=article.title,
            body=article.excerpt or "Nuevo artículo publicado.",
            data={
                "type": "new_article",
                "article_id": str(article.id),
                "slug": article.slug,
            },
        )

        logger.info(
            "FCM enviado para artículo %s. Éxitos: %s, fallos: %s.",
            article.id,
            response.success_count,
            response.failure_count,
        )

        db.refresh(event)

        mark_event_sent(
            db=db,
            event=event,
        )

        db.commit()

        return True

    except Exception as exc:
        db.rollback()

        event = db.get(
            type(event),
            event.id,
        )

        if event is None:
            logger.error(
                "No se pudo recuperar el evento después del error."
            )

            return False

        mark_event_failed(
            db=db,
            event=event,
            error=str(exc),
        )

        db.commit()

        logger.exception(
            "Error enviando FCM para artículo %s.",
            article.id,
        )

        return False


def run_notification_worker() -> int:
    db = SessionLocal()

    processed = 0

    try:
        recovered = recover_stuck_notification_events(
            db=db,
        )

        if recovered > 0:
            logger.warning(
                "Eventos processing recuperados: %s",
                recovered,
            )

            db.commit()

        events = get_pending_notification_events(
            db=db,
            limit=BATCH_SIZE,
        )

        if not events:
            logger.info(
                "No hay eventos de notificación pendientes."
            )

            db.rollback()

            return 0

        for event in events:
            try:
                process_notification_event(
                    db=db,
                    event=event,
                )

                processed += 1

            except Exception:
                db.rollback()

                logger.exception(
                    "Error procesando evento de notificación %s.",
                    event.id,
                )

        return processed

    except Exception:
        db.rollback()

        logger.exception(
            "Error durante la ejecución del notification worker."
        )

        return processed

    finally:
        db.close()


def main() -> None:
    logger.info(
        "Notification Worker iniciado. Intervalo: %s segundos.",
        WORKER_INTERVAL,
    )

    while True:
        run_notification_worker()

        time.sleep(
            WORKER_INTERVAL
        )


if __name__ == "__main__":
    main()
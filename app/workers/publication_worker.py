import logging
import os
import time

from app.core.database import SessionLocal
from app.services.publishing import publish_scheduled_articles


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [PUBLICATION WORKER] %(levelname)s: %(message)s",
)

logger = logging.getLogger(__name__)


WORKER_INTERVAL = int(
    os.getenv("PUBLICATION_WORKER_INTERVAL", "30")
)


def run_publication_worker() -> int:
    db = SessionLocal()

    try:
        published = publish_scheduled_articles(db=db)

        if published > 0:
            logger.info(
                "Artículos publicados automáticamente: %s",
                published,
            )
        else:
            logger.info(
                "No hay artículos pendientes de publicación."
            )

        return published

    except Exception:
        db.rollback()
        logger.exception(
            "Error durante la ejecución del publication worker."
        )
        return 0

    finally:
        db.close()


def main() -> None:
    logger.info(
        "Publication Worker iniciado. Intervalo: %s segundos.",
        WORKER_INTERVAL,
    )

    while True:
        run_publication_worker()
        time.sleep(WORKER_INTERVAL)


if __name__ == "__main__":
    main()
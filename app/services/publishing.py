from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.article import Article
from app.services.article_history import record_article_history
from app.services.notification_events import create_notification_event

# ============================================================
# GET SCHEDULED ARTICLES
# ============================================================

def get_scheduled_articles(
    db: Session,
    now: datetime | None = None,
) -> list[Article]:

    if now is None:
        now = datetime.now(timezone.utc)

    stmt = (
        select(Article)
        .where(
            Article.status == "scheduled",
            Article.scheduled_at.is_not(None),
            Article.scheduled_at <= now,
        )
        .order_by(
            Article.scheduled_at.asc()
        )
    )

    return db.execute(
        stmt
    ).scalars().all()


# ============================================================
# PUBLISH SCHEDULED ARTICLES
# ============================================================

def publish_scheduled_articles(
    db: Session,
    now: datetime | None = None,
) -> int:

    if now is None:
        now = datetime.now(timezone.utc)

    articles = get_scheduled_articles(
        db=db,
        now=now,
    )

    if not articles:
        return 0

    for article in articles:

        previous_status = article.status

        article.status = "published"
        article.published_at = now
        article.scheduled_at = None

        record_article_history(
            db=db,
            article_id=article.id,
            action="publish",
            from_status=previous_status,
            to_status="published",
            user_id=None,
            actor_type="system",
        )
        create_notification_event(
            db=db,
            article_id=article.id,
        )
    db.commit()

    return len(articles)
from sqlalchemy.orm import Session

from app.models.article_history import ArticleHistory


def record_article_history(
    db: Session,
    article_id: int,
    action: str,
    from_status: str | None = None,
    to_status: str | None = None,
    user_id: int | None = None,
    actor_type: str = "user",
) -> ArticleHistory:

    history = ArticleHistory(
        article_id=article_id,
        user_id=user_id,
        actor_type=actor_type,
        action=action,
        from_status=from_status,
        to_status=to_status,
    )

    db.add(history)

    return history


def get_article_history(
    db: Session,
    article_id: int,
) -> list[ArticleHistory]:

    return (
        db.query(ArticleHistory)
        .filter(
            ArticleHistory.article_id == article_id
        )
        .order_by(
            ArticleHistory.created_at.desc()
        )
        .all()
    )
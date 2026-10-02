from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.article import Article
from app.models.favorite import Favorite


def get_user_favorites(
    db: Session,
    user_id: int,
) -> list[Favorite]:

    stmt = (
        select(Favorite)
        .join(Favorite.article)
        .options(
            joinedload(Favorite.article),
        )
        .where(
            Favorite.user_id == user_id,
            Article.status == "published",
        )
        .order_by(
            Favorite.created_at.desc(),
        )
    )

    return db.execute(stmt).scalars().unique().all()


def get_favorite(
    db: Session,
    user_id: int,
    article_id: int,
) -> Favorite | None:

    stmt = select(Favorite).where(
        Favorite.user_id == user_id,
        Favorite.article_id == article_id,
    )

    return db.execute(stmt).scalar_one_or_none()


def add_favorite(
    db: Session,
    user_id: int,
    article_id: int,
) -> Favorite:

    article = db.get(
        Article,
        article_id,
    )

    if article is None:
        raise ValueError("Article not found")

    if article.status != "published":
        raise ValueError(
            "Only published articles can be added to favorites"
        )

    existing = get_favorite(
        db=db,
        user_id=user_id,
        article_id=article_id,
    )

    if existing is not None:
        raise ValueError(
            "Article is already in favorites"
        )

    favorite = Favorite(
        user_id=user_id,
        article_id=article_id,
    )

    db.add(favorite)
    db.commit()
    db.refresh(favorite)

    return favorite


def remove_favorite(
    db: Session,
    user_id: int,
    article_id: int,
) -> bool:

    favorite = get_favorite(
        db=db,
        user_id=user_id,
        article_id=article_id,
    )

    if favorite is None:
        return False

    db.delete(favorite)
    db.commit()

    return True
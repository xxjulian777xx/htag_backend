from sqlalchemy import Text, cast, exists, func, or_, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.article import Article
from app.models.article_block import ArticleBlock
from app.models.category import Category
from app.models.tag import Tag


def get_reader_article_query():
    return (
        select(Article)
        .options(
            joinedload(Article.category),
            joinedload(Article.cover_media),
            selectinload(Article.tags),
        )
        .where(
            Article.status == "published",
        )
    )


def get_reader_article_detail_query():
    return (
        select(Article)
        .options(
            joinedload(Article.category),
            joinedload(Article.cover_media),
            selectinload(Article.tags),
            selectinload(Article.blocks),
        )
        .where(
            Article.status == "published",
        )
    )


def list_reader_articles(
    db: Session,
    *,
    page: int = 1,
    page_size: int = 20,
    category_id: int | None = None,
    tag_id: int | None = None,
) -> dict:

    filters = []

    if category_id is not None:
        filters.append(
            Article.category_id == category_id
        )

    if tag_id is not None:
        filters.append(
            Article.tags.any(Tag.id == tag_id)
        )

    count_stmt = (
        select(func.count(Article.id))
        .where(
            Article.status == "published",
        )
    )

    if filters:
        count_stmt = count_stmt.where(*filters)

    total = db.execute(
        count_stmt
    ).scalar_one()

    offset = (page - 1) * page_size

    stmt = (
        get_reader_article_query()
        .where(*filters)
        .order_by(
            Article.published_at.desc(),
            Article.id.desc(),
        )
        .offset(offset)
        .limit(page_size)
    )

    items = (
        db.execute(stmt)
        .scalars()
        .unique()
        .all()
    )

    pages = (
        (total + page_size - 1) // page_size
        if total
        else 0
    )

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": pages,
    }


def get_reader_article_by_slug(
    db: Session,
    slug: str,
) -> Article | None:

    stmt = (
        get_reader_article_detail_query()
        .where(
            Article.slug == slug,
        )
    )

    return (
        db.execute(stmt)
        .scalars()
        .unique()
        .one_or_none()
    )


def get_reader_article_of_the_day(
    db: Session,
) -> Article | None:

    stmt = (
        get_reader_article_detail_query()
        .where(
            Article.is_featured.is_(True),
        )
        .order_by(
            Article.published_at.desc(),
            Article.id.desc(),
        )
        .limit(1)
    )

    return (
        db.execute(stmt)
        .scalars()
        .unique()
        .first()
    )


def search_reader_articles(
    db: Session,
    *,
    query: str,
    page: int = 1,
    page_size: int = 20,
) -> dict:

    search = query.strip()

    if not search:
        return {
            "items": [],
            "total": 0,
            "page": page,
            "page_size": page_size,
            "pages": 0,
        }

    pattern = f"%{search}%"

    block_match = exists(
        select(ArticleBlock.id)
        .where(
            ArticleBlock.article_id == Article.id,
            cast(
                ArticleBlock.data,
                Text,
            ).ilike(pattern),
        )
    )

    category_match = exists(
        select(Category.id)
        .where(
            Category.id == Article.category_id,
            Category.name.ilike(pattern),
        )
    )

    tag_match = exists(
        select(Tag.id)
        .where(
            Tag.articles.any(
                Article.id == Article.id
            ),
            Tag.name.ilike(pattern),
        )
    )

    search_filter = or_(
        Article.title.ilike(pattern),
        Article.slug.ilike(pattern),
        Article.excerpt.ilike(pattern),
        Article.seo_title.ilike(pattern),
        Article.seo_description.ilike(pattern),
        block_match,
        category_match,
        tag_match,
    )

    count_stmt = (
        select(func.count(Article.id))
        .where(
            Article.status == "published",
            search_filter,
        )
    )

    total = db.execute(
        count_stmt
    ).scalar_one()

    offset = (page - 1) * page_size

    stmt = (
        get_reader_article_query()
        .where(
            search_filter,
        )
        .order_by(
            Article.published_at.desc(),
            Article.id.desc(),
        )
        .offset(offset)
        .limit(page_size)
    )

    items = (
        db.execute(stmt)
        .scalars()
        .unique()
        .all()
    )

    pages = (
        (total + page_size - 1) // page_size
        if total
        else 0
    )

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": pages,
    }
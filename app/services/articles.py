from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models.article import Article
from app.models.article_block import ArticleBlock
from app.models.category import Category
from app.models.media import Media
from app.models.tag import Tag
from app.models.user import User
from app.schemas.article import (
    ArticleCreate,
    ArticleUpdate,
)
from app.services.article_history import record_article_history
from app.services.notification_events import create_notification_event

# ============================================================
# ARTICLE QUERY
# ============================================================

def get_article_query():
    return (
        select(Article)
        .options(
            selectinload(Article.blocks),
            selectinload(Article.tags),
        )
    )


# ============================================================
# GET ARTICLE
# ============================================================

def get_article(
    db: Session,
    article_id: int,
) -> Article | None:

    stmt = (
        get_article_query()
        .where(Article.id == article_id)
    )

    return db.execute(stmt).scalar_one_or_none()


# ============================================================
# GET ARTICLE BY SLUG
# ============================================================

def get_article_by_slug(
    db: Session,
    slug: str,
) -> Article | None:

    stmt = (
        get_article_query()
        .where(Article.slug == slug)
    )

    return db.execute(stmt).scalar_one_or_none()


# ============================================================
# VALIDATE SLUG
# ============================================================

def validate_slug(
    db: Session,
    slug: str,
    article_id: int | None = None,
) -> None:

    stmt = select(Article.id).where(
        Article.slug == slug
    )

    if article_id is not None:
        stmt = stmt.where(
            Article.id != article_id
        )

    existing = db.execute(
        stmt
    ).scalar_one_or_none()

    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Article slug already exists",
        )


# ============================================================
# VALIDATE CATEGORY
# ============================================================

def validate_category(
    db: Session,
    category_id: int | None,
) -> None:

    if category_id is None:
        return

    category = db.execute(
        select(Category).where(
            Category.id == category_id
        )
    ).scalar_one_or_none()

    if category is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category not found",
        )

    if not category.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category is inactive",
        )


# ============================================================
# VALIDATE MEDIA
# ============================================================

def validate_media(
    db: Session,
    media_id: int | None,
) -> None:

    if media_id is None:
        return

    media = db.execute(
        select(Media).where(
            Media.id == media_id
        )
    ).scalar_one_or_none()

    if media is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cover media not found",
        )


# ============================================================
# VALIDATE AUTHOR
# ============================================================

def validate_author(
    db: Session,
    author_id: int | None,
) -> None:

    if author_id is None:
        return

    author = db.execute(
        select(User).where(
            User.id == author_id
        )
    ).scalar_one_or_none()

    if author is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Author not found",
        )

    if not author.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Author is inactive",
        )


# ============================================================
# VALIDATE TAGS
# ============================================================

def validate_tags(
    db: Session,
    tag_ids: list[int],
) -> list[Tag]:

    if not tag_ids:
        return []

    unique_tag_ids = list(
        dict.fromkeys(tag_ids)
    )

    tags = db.execute(
        select(Tag).where(
            Tag.id.in_(unique_tag_ids)
        )
    ).scalars().all()

    found_ids = {
        tag.id
        for tag in tags
    }

    missing_ids = [
        tag_id
        for tag_id in unique_tag_ids
        if tag_id not in found_ids
    ]

    if missing_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "One or more tags were not found",
                "tag_ids": missing_ids,
            },
        )

    return list(tags)


# ============================================================
# CREATE ARTICLE
# ============================================================

def create_article(
    db: Session,
    data: ArticleCreate,
    user_id: int | None = None,
) -> Article:
    
    validate_slug(db=db, slug=data.slug)
    validate_category(db=db, category_id=data.category_id)
    validate_media(db=db, media_id=data.cover_media_id)
    validate_author(db=db, author_id=data.author_id)

    tags = validate_tags(
        db=db,
        tag_ids=data.tag_ids,
    )

    article = Article(
        title=data.title,
        slug=data.slug,
        excerpt=data.excerpt,
        status="draft",
        author_id=data.author_id,
        category_id=data.category_id,
        cover_media_id=data.cover_media_id,
        scheduled_at=None,
        published_at=None,
        is_featured=data.is_featured,
        allow_comments=data.allow_comments,
        seo_title=data.seo_title,
        seo_description=data.seo_description,
    )

    db.add(article)
    db.flush()
    record_article_history(
        db=db,
        article_id=article.id,
        action="create",
        from_status=None,
        to_status="draft",
        user_id=user_id,
        actor_type="user",
    )
    
    for block_data in data.blocks:
        block = ArticleBlock(
            article_id=article.id,
            block_type=block_data.block_type,
            position=block_data.position,
            data=block_data.data,
        )
        db.add(block)

    article.tags = tags

    db.commit()

    return get_article(db, article.id)

# ============================================================
# UPDATE ARTICLE
# ============================================================

def update_article(
    db: Session,
    article_id: int,
    data: ArticleUpdate,
    user_id: int | None = None,
) -> Article | None:

    article = get_article(
        db,
        article_id,
    )

    if article is None:
        return None
    previous_status = article.status
    resulting_category_id = (
        data.category_id
        if data.category_id is not None
        else article.category_id
    )

    resulting_cover_media_id = (
        data.cover_media_id
        if data.cover_media_id is not None
        else article.cover_media_id
    )

    resulting_author_id = (
        data.author_id
        if data.author_id is not None
        else article.author_id
    )

    resulting_slug = (
        data.slug
        if data.slug is not None
        else article.slug
    )

    if data.slug is not None:
        validate_slug(
            db=db,
            slug=resulting_slug,
            article_id=article.id,
        )

    if data.category_id is not None:
        validate_category(
            db=db,
            category_id=resulting_category_id,
        )

    if data.cover_media_id is not None:
        validate_media(
            db=db,
            media_id=resulting_cover_media_id,
        )

    if data.author_id is not None:
        validate_author(
            db=db,
            author_id=resulting_author_id,
        )

    update_data = data.model_dump(
        exclude_unset=True,
        exclude={
            "blocks",
            "tag_ids",
        },
    )

    for field, value in update_data.items():
        setattr(
            article,
            field,
            value,
        )

    if data.blocks is not None:

        article.blocks.clear()

        db.flush()

        for block_data in data.blocks:

            block = ArticleBlock(
                article_id=article.id,
                block_type=block_data.block_type,
                position=block_data.position,
                data=block_data.data,
            )

            db.add(block)

    if data.tag_ids is not None:

        tags = validate_tags(
            db=db,
            tag_ids=data.tag_ids,
        )

        article.tags = tags

    record_article_history(
        db=db,
        article_id=article.id,
        action="update",
        from_status=previous_status,
        to_status=article.status,
        user_id=user_id,
        actor_type="user",
    )
    db.commit()

    return get_article(
        db,
        article.id,
    )


# ============================================================
# SCHEDULE ARTICLE
# ============================================================

def schedule_article(
    db: Session,
    article_id: int,
    scheduled_at: datetime,
    user_id: int | None = None,
) -> Article | None:

    article = get_article(
        db,
        article_id,
    )

    if article is None:
        return None
    previous_status = article.status
    if article.status == "published":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Published articles cannot be scheduled",
        )

    if article.status == "archived":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Archived articles cannot be scheduled",
        )

    if scheduled_at <= datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="scheduled_at must be in the future",
        )
    
    article.status = "scheduled"
    article.scheduled_at = scheduled_at
    article.published_at = None
    record_article_history(
        db=db,
        article_id=article.id,
        action="schedule",
        from_status=previous_status,
        to_status="scheduled",
        user_id=user_id,
        actor_type="user",
    )
    db.commit()

    return get_article(
        db,
        article.id,
    )


# ============================================================
# PUBLISH ARTICLE
# ============================================================

def publish_article(
    db: Session,
    article_id: int,
    published_at: datetime | None = None,
    user_id: int | None = None,
    actor_type: str = "user",
) -> Article | None:

    article = get_article(
        db,
        article_id,
    )

    if article is None:
        return None

    if article.status == "published":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Article is already published",
        )

    if article.status == "archived":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Archived articles cannot be published",
        )

    publication_time = (
        published_at
        if published_at is not None
        else datetime.now(timezone.utc)
    )
    previous_status = article.status
    article.status = "published"
    article.published_at = publication_time

    if article.scheduled_at is not None:
        article.scheduled_at = None

    record_article_history(
        db=db,
        article_id=article.id,
        action="publish",
        from_status=previous_status,
        to_status="published",
        user_id=user_id,
        actor_type=actor_type,
    )
    create_notification_event(
        db=db,
        article_id=article.id,
    )
    db.commit()

    return get_article(
        db,
        article.id,
    )


# ============================================================
# DELETE ARTICLE
# ============================================================

def delete_article(
    db: Session,
    article_id: int,
) -> bool:

    article = get_article(
        db,
        article_id,
    )

    if article is None:
        return False

    db.delete(article)

    db.commit()

    return True


# ============================================================
# LIST ARTICLES
# ============================================================

def list_articles(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    status: str | None = None,
    category_id: int | None = None,
):

    if page < 1:
        page = 1

    if page_size < 1:
        page_size = 20

    if page_size > 100:
        page_size = 100

    filters = []

    if status is not None:
        filters.append(
            Article.status == status
        )

    if category_id is not None:
        filters.append(
            Article.category_id == category_id
        )

    count_stmt = select(
        func.count(Article.id)
    )

    if filters:
        count_stmt = count_stmt.where(
            *filters
        )

    total = db.execute(
        count_stmt
    ).scalar_one()

    offset = (
        page - 1
    ) * page_size

    stmt = (
        get_article_query()
        .order_by(
            Article.created_at.desc()
        )
        .offset(offset)
        .limit(page_size)
    )

    if filters:
        stmt = stmt.where(
            *filters
        )

    items = db.execute(
        stmt
    ).scalars().unique().all()

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

def archive_article(
    db: Session,
    article_id: int,
    user_id: int | None = None,
) -> Article | None:
    article = get_article(db, article_id)

    if article is None:
        return None

    if article.status == "archived":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Article is already archived",
        )

    if article.status != "published":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only published articles can be archived",
        )
    previous_status = article.status
    article.status = "archived"
    record_article_history(
        db=db,
        article_id=article.id,
        action="archive",
        from_status=previous_status,
        to_status="archived",
        user_id=user_id,
        actor_type="user",
    )
    db.commit()

    return get_article(db, article.id)

# ============================================================
# RESCHEDULE ARTICLE
# ============================================================

def reschedule_article(
    db: Session,
    article_id: int,
    scheduled_at: datetime,
    user_id: int | None = None,
) -> Article | None:

    article = get_article(
        db,
        article_id,
    )

    if article is None:
        return None

    if article.status != "scheduled":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only scheduled articles can be rescheduled",
        )

    if scheduled_at <= datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="scheduled_at must be in the future",
        )

    article.scheduled_at = scheduled_at
    article.published_at = None

    record_article_history(
        db=db,
        article_id=article.id,
        action="reschedule",
        from_status="scheduled",
        to_status="scheduled",
        user_id=user_id,
        actor_type="user",
    )

    db.commit()

    return get_article(
        db,
        article.id,
    )
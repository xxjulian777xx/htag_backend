from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import (
    get_db,
    require_permission,
)
from app.models.user import User
from app.schemas.article import (
    ArticleCreate,
    ArticlePublish,
    ArticleResponse,
    ArticleSchedule,
    ArticleUpdate,
)
from app.schemas.articles import ArticleListResponse
from app.services.articles import (
    archive_article,
    create_article,
    delete_article,
    get_article,
    get_article_by_slug,
    list_articles,
    publish_article,
    reschedule_article,
    schedule_article,
    update_article,
)
from app.schemas.article_history import ArticleHistoryResponse
from app.services.article_history import get_article_history

router = APIRouter(
    prefix="/v1/articles",
    tags=["Articles"],
)


# ============================================================
# LIST
# ============================================================

@router.get(
    "",
    response_model=ArticleListResponse,
)
def get_articles(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    status_filter: str | None = Query(
        default=None,
        alias="status",
    ),
    category_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("articles.read")
    ),
):
    return list_articles(
        db=db,
        page=page,
        page_size=page_size,
        status=status_filter,
        category_id=category_id,
    )


# ============================================================
# GET BY ID
# ============================================================

@router.get(
    "/{article_id}",
    response_model=ArticleResponse,
)
def get_article_by_id(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("articles.read")
    ),
):
    article = get_article(
        db,
        article_id,
    )

    if article is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found",
        )

    return article


# ============================================================
# GET BY SLUG
# ============================================================

@router.get(
    "/slug/{slug}",
    response_model=ArticleResponse,
)
def get_article_by_slug_endpoint(
    slug: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("articles.read")
    ),
):
    article = get_article_by_slug(
        db,
        slug,
    )

    if article is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found",
        )

    return article


# ============================================================
# CREATE
# ============================================================

@router.post(
    "",
    response_model=ArticleResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_article_endpoint(
    data: ArticleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("articles.create")
    ),
):
    existing = get_article_by_slug(
        db,
        data.slug,
    )

    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Article slug already exists",
        )

    return create_article(
        db=db,
        data=data,
        user_id=current_user.id,
    )


# ============================================================
# UPDATE CONTENT / METADATA
# ============================================================

@router.put(
    "/{article_id}",
    response_model=ArticleResponse,
)
def update_article_endpoint(
    article_id: int,
    data: ArticleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("articles.update")
    ),
):
    if data.slug is not None:
        existing = get_article_by_slug(
            db,
            data.slug,
        )

        if (
            existing is not None
            and existing.id != article_id
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Article slug already exists",
            )

    article = update_article(
        db=db,
        article_id=article_id,
        data=data,
        user_id=current_user.id,
    )

    if article is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found",
        )

    return article


# ============================================================
# SCHEDULE
# ============================================================

@router.post(
    "/{article_id}/schedule",
    response_model=ArticleResponse,
)
def schedule_article_endpoint(
    article_id: int,
    data: ArticleSchedule,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("articles.schedule")
    ),
):
    article = schedule_article(
        db=db,
        article_id=article_id,
        scheduled_at=data.scheduled_at,
        user_id=current_user.id,
    )

    if article is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found",
        )

    return article


# ============================================================
# PUBLISH
# ============================================================

@router.post(
    "/{article_id}/publish",
    response_model=ArticleResponse,
)
def publish_article_endpoint(
    article_id: int,
    data: ArticlePublish,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("articles.publish")
    ),
):
    article = publish_article(
        db=db,
        article_id=article_id,
        published_at=data.published_at,
        user_id=current_user.id,
        actor_type="user",
    )

    if article is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found",
        )

    return article


@router.post(
    "/{article_id}/archive",
    response_model=ArticleResponse,
)
def archive_article_endpoint(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("articles.archive")
    ),
):
    article = archive_article(
        db=db,
        article_id=article_id,
        user_id=current_user.id,
    )

    if article is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found",
        )

    return article

# ============================================================
# DELETE
# ============================================================

@router.delete(
    "/{article_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_article_endpoint(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("articles.delete")
    ),
):
    deleted = delete_article(
        db,
        article_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found",
        )

    return None

# ============================================================
# HISTORY
# ============================================================

@router.get(
    "/{article_id}/history",
    response_model=list[ArticleHistoryResponse],
)
def get_article_history_endpoint(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("articles.read")
    ),
):
    article = get_article(
        db,
        article_id,
    )

    if article is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found",
        )

    return get_article_history(
        db=db,
        article_id=article_id,
    )

# ============================================================
# RESCHEDULE
# ============================================================

@router.post(
    "/{article_id}/reschedule",
    response_model=ArticleResponse,
)
def reschedule_article_endpoint(
    article_id: int,
    data: ArticleSchedule,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("articles.schedule")
    ),
):
    article = reschedule_article(
        db=db,
        article_id=article_id,
        scheduled_at=data.scheduled_at,
        user_id=current_user.id,
    )

    if article is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found",
        )

    return article
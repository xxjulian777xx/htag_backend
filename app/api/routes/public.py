from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.category import Category
from app.models.tag import Tag
from app.schemas.category import CategoryResponse
from app.schemas.reader import (
    ReaderArticleListResponse,
    ReaderArticleResponse,
)
from app.schemas.tag import TagResponse
from app.services.reader import (
    get_reader_article_by_slug,
    get_reader_article_of_the_day,
    list_reader_articles,
    search_reader_articles,
)

router = APIRouter(
    prefix="/v1/public",
    tags=["Public"],
)


@router.get(
    "/articles",
    response_model=ReaderArticleListResponse,
)
def get_public_articles(
    page: int = Query(
        default=1,
        ge=1,
    ),
    page_size: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    category_id: int | None = Query(
        default=None,
        ge=1,
    ),
    tag_id: int | None = Query(
        default=None,
        ge=1,
    ),
    db: Session = Depends(get_db),
):
    return list_reader_articles(
        db=db,
        page=page,
        page_size=page_size,
        category_id=category_id,
        tag_id=tag_id,
    )


@router.get(
    "/articles/today",
    response_model=ReaderArticleResponse,
)
def get_article_of_the_day(
    db: Session = Depends(get_db),
):
    article = get_reader_article_of_the_day(
        db=db,
    )

    if article is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No published featured articles available",
        )

    return article


@router.get(
    "/articles/{slug}",
    response_model=ReaderArticleResponse,
)
def get_public_article_by_slug(
    slug: str,
    db: Session = Depends(get_db),
):
    article = get_reader_article_by_slug(
        db=db,
        slug=slug,
    )

    if article is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found",
        )

    return article


@router.get(
    "/categories",
    response_model=list[CategoryResponse],
)
def get_public_categories(
    db: Session = Depends(get_db),
):
    return (
        db.execute(
            select(Category)
            .where(
                Category.is_active.is_(True)
            )
            .order_by(
                Category.sort_order.asc(),
                Category.name.asc(),
            )
        )
        .scalars()
        .all()
    )


@router.get(
    "/categories/{slug}",
    response_model=CategoryResponse,
)
def get_public_category_by_slug(
    slug: str,
    db: Session = Depends(get_db),
):
    category = db.execute(
        select(Category)
        .where(
            Category.slug == slug,
            Category.is_active.is_(True),
        )
    ).scalar_one_or_none()

    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )

    return category


@router.get(
    "/tags",
    response_model=list[TagResponse],
)
def get_public_tags(
    db: Session = Depends(get_db),
):
    return (
        db.execute(
            select(Tag)
            .order_by(
                Tag.name.asc()
            )
        )
        .scalars()
        .all()
    )


@router.get(
    "/tags/{slug}",
    response_model=TagResponse,
)
def get_public_tag_by_slug(
    slug: str,
    db: Session = Depends(get_db),
):
    tag = db.execute(
        select(Tag)
        .where(
            Tag.slug == slug
        )
    ).scalar_one_or_none()

    if tag is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found",
        )

    return tag


@router.get(
    "/search",
    response_model=ReaderArticleListResponse,
)
def search_public_articles(
    q: str = Query(
        ...,
        min_length=1,
        max_length=100,
    ),
    page: int = Query(
        default=1,
        ge=1,
    ),
    page_size: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    db: Session = Depends(get_db),
):
    search_term = q.strip()

    if not search_term:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search query cannot be empty",
        )

    return search_reader_articles(
        db=db,
        query=search_term,
        page=page,
        page_size=page_size,
    )
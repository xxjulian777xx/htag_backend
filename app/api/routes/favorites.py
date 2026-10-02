from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.favorite import FavoriteResponse
from app.services.favorites import (
    add_favorite,
    get_user_favorites,
    remove_favorite,
)


router = APIRouter(
    prefix="/v1/reader/favorites",
    tags=["Reader Favorites"],
)


@router.get(
    "",
    response_model=list[FavoriteResponse],
)
def list_favorites(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_user_favorites(
        db=db,
        user_id=current_user.id,
    )


@router.post(
    "/{article_id}",
    response_model=FavoriteResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_favorite(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return add_favorite(
            db=db,
            user_id=current_user.id,
            article_id=article_id,
        )

    except ValueError as exc:
        message = str(exc)

        if message == "Article not found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=message,
            )

        if message == "Article is already in favorites":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=message,
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        )


@router.delete(
    "/{article_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_favorite(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    removed = remove_favorite(
        db=db,
        user_id=current_user.id,
        article_id=article_id,
    )

    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Favorite not found",
        )

    return None
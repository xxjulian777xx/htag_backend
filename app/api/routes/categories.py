from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import (
    get_db,
    require_permission,
)
from app.models.user import User
from app.schemas.category import (
    CategoryCreate,
    CategoryResponse,
    CategoryUpdate,
)
from app.services.categories import (
    create_category,
    delete_category,
    get_category,
    list_categories,
    update_category,
)


router = APIRouter(
    prefix="/v1/categories",
    tags=["Categories"],
)


@router.get(
    "",
    response_model=list[CategoryResponse],
)
def get_categories(
    active_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("categories.read")
    ),
):
    return list_categories(
        db,
        active_only=active_only,
    )


@router.get(
    "/{category_id}",
    response_model=CategoryResponse,
)
def get_category_by_id(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("categories.read")
    ),
):
    category = get_category(
        db,
        category_id,
    )

    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )

    return category


@router.post(
    "",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_category_endpoint(
    data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("categories.create")
    ),
):
    return create_category(
        db,
        data,
    )


@router.put(
    "/{category_id}",
    response_model=CategoryResponse,
)
def update_category_endpoint(
    category_id: int,
    data: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("categories.update")
    ),
):
    category = update_category(
        db,
        category_id,
        data,
    )

    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )

    return category


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_category_endpoint(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("categories.delete")
    ),
):
    deleted = delete_category(
        db,
        category_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )
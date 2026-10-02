from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import (
    get_db,
    require_permission,
)
from app.models.user import User
from app.schemas.tag import (
    TagCreate,
    TagResponse,
    TagUpdate,
)
from app.services.tags import (
    create_tag,
    delete_tag,
    get_tag,
    list_tags,
    update_tag,
)


router = APIRouter(
    prefix="/v1/tags",
    tags=["Tags"],
)


@router.get(
    "",
    response_model=list[TagResponse],
)
def get_tags(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("tags.read")
    ),
):
    return list_tags(db)


@router.get(
    "/{tag_id}",
    response_model=TagResponse,
)
def get_tag_by_id(
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("tags.read")
    ),
):
    tag = get_tag(
        db,
        tag_id,
    )

    if tag is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found",
        )

    return tag


@router.post(
    "",
    response_model=TagResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_tag_endpoint(
    data: TagCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("tags.create")
    ),
):
    return create_tag(
        db,
        data,
    )


@router.put(
    "/{tag_id}",
    response_model=TagResponse,
)
def update_tag_endpoint(
    tag_id: int,
    data: TagUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("tags.update")
    ),
):
    tag = update_tag(
        db,
        tag_id,
        data,
    )

    if tag is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found",
        )

    return tag


@router.delete(
    "/{tag_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_tag_endpoint(
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("tags.delete")
    ),
):
    deleted = delete_tag(
        db,
        tag_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found",
        )
from pathlib import Path
from uuid import uuid4
from datetime import datetime

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.api.dependencies import (
    get_db,
    require_permission,
)
from app.models.user import User
from app.schemas.media import MediaResponse
from app.services.media import (
    create_media,
    delete_media,
    get_media,
    list_media,
    update_media,
)
from app.services.storage import upload_bytes


router = APIRouter(
    prefix="/v1/media",
    tags=["Media"],
)


@router.get(
    "",
    response_model=list[MediaResponse],
)
def get_media_list(
    mime_type: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("media.read")
    ),
):
    return list_media(
        db=db,
        mime_type=mime_type,
    )


@router.get(
    "/{media_id}",
    response_model=MediaResponse,
)
def get_media_by_id(
    media_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("media.read")
    ),
):
    media = get_media(
        db=db,
        media_id=media_id,
    )

    if media is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Media not found",
        )

    return media


@router.post(
    "",
    response_model=MediaResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_media_endpoint(
    file: UploadFile = File(...),
    title: str | None = Form(default=None),
    alt_text: str | None = Form(default=None),
    description: str | None = Form(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("media.upload")
    ),
):
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is required",
        )

    if not file.content_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Content type is required",
        )

    file_data = await file.read()

    if not file_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File is empty",
        )

    original_filename = Path(file.filename).name

    extension = Path(original_filename).suffix.lower()

    stored_filename = f"{uuid4().hex}{extension}"

    object_key = (
        f"media/"
        f"{datetime.now().strftime('%Y/%m')}/"
        f"{stored_filename}"
    )

    try:
        upload_bytes(
            data=file_data,
            object_key=object_key,
            content_type=file.content_type,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Unable to store file: {exc}",
        ) from exc

    try:
        media = create_media(
            db=db,
            original_filename=original_filename,
            stored_filename=stored_filename,
            storage_path=object_key,
            mime_type=file.content_type,
            size_bytes=len(file_data),
            url=None,
            title=title,
            alt_text=alt_text,
            description=description,
            uploaded_by=current_user.id,
        )

        return media

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to create media record: {exc}",
        ) from exc


@router.put(
    "/{media_id}",
    response_model=MediaResponse,
)
def update_media_endpoint(
    media_id: int,
    title: str | None = Form(default=None),
    alt_text: str | None = Form(default=None),
    description: str | None = Form(default=None),
    url: str | None = Form(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("media.update")
    ),
):
    media = update_media(
        db=db,
        media_id=media_id,
        title=title,
        alt_text=alt_text,
        description=description,
        url=url,
    )

    if media is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Media not found",
        )

    return media


@router.delete(
    "/{media_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_media_endpoint(
    media_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("media.delete")
    ),
):
    deleted = delete_media(
        db=db,
        media_id=media_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Media not found",
        )

    return None
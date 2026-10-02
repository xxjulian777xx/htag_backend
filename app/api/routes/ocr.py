from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import (
    get_db,
    require_permission,
)
from app.models.user import User
from app.schemas.ocr import (
    OCRProcessRequest,
    OCRResponse,
)
from app.services.ocr import (
    get_ocr,
    list_ocr,
    process_ocr,
)


router = APIRouter(
    prefix="/v1/ocr",
    tags=["OCR"],
)


@router.get(
    "",
    response_model=list[OCRResponse],
)
def get_ocr_list(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("ocr.read")
    ),
):
    return list_ocr(db)


@router.get(
    "/{ocr_id}",
    response_model=OCRResponse,
)
def get_ocr_by_id(
    ocr_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("ocr.read")
    ),
):
    ocr_document = get_ocr(
        db=db,
        ocr_id=ocr_id,
    )

    if ocr_document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="OCR document not found",
        )

    return ocr_document


@router.post(
    "/process",
    response_model=OCRResponse,
    status_code=status.HTTP_201_CREATED,
)
def process_ocr_endpoint(
    data: OCRProcessRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("ocr.process")
    ),
):
    try:
        return process_ocr(
            db=db,
            media_id=data.media_id,
            processed_by=current_user.id,
            language=data.language,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OCR processing failed: {exc}",
        ) from exc
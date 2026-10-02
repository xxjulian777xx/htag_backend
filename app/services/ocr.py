from datetime import datetime, timezone
from io import BytesIO

import pytesseract
from PIL import Image
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.media import Media
from app.models.ocr import OCRDocument
from app.services.storage import download_object


def get_ocr(
    db: Session,
    ocr_id: int,
) -> OCRDocument | None:
    stmt = select(OCRDocument).where(
        OCRDocument.id == ocr_id
    )

    return db.execute(stmt).scalar_one_or_none()


def list_ocr(
    db: Session,
) -> list[OCRDocument]:
    stmt = select(OCRDocument).order_by(
        OCRDocument.created_at.desc()
    )

    return db.execute(stmt).scalars().all()


def process_ocr(
    db: Session,
    *,
    media_id: int,
    processed_by: int,
    language: str = "spa+eng",
) -> OCRDocument:

    media = db.execute(
        select(Media).where(Media.id == media_id)
    ).scalar_one_or_none()

    if media is None:
        raise ValueError("Media not found")

    if not media.mime_type.startswith("image/"):
        raise ValueError(
            "OCR currently supports image files only"
        )

    ocr_document = OCRDocument(
        media_id=media.id,
        status="processing",
        processed_by=processed_by,
    )

    db.add(ocr_document)
    db.commit()
    db.refresh(ocr_document)

    try:
        file_data = download_object(
            media.storage_path
        )

        image = Image.open(
            BytesIO(file_data)
        )

        image.load()

        extracted_text = pytesseract.image_to_string(
            image,
            lang=language,
        )

        ocr_document.status = "processed"
        ocr_document.extracted_text = extracted_text
        ocr_document.error_message = None
        ocr_document.processed_at = datetime.now(
            timezone.utc
        )

        db.commit()
        db.refresh(ocr_document)

        return ocr_document

    except Exception as exc:

        db.rollback()

        ocr_document = db.get(
            OCRDocument,
            ocr_document.id,
        )

        if ocr_document is not None:
            ocr_document.status = "failed"
            ocr_document.error_message = str(exc)
            ocr_document.processed_at = datetime.now(
                timezone.utc
            )

            db.commit()
            db.refresh(ocr_document)

        raise
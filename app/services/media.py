from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.media import Media
from app.services.storage import delete_object


def get_media(
    db: Session,
    media_id: int,
) -> Media | None:
    stmt = select(Media).where(Media.id == media_id)

    return db.execute(stmt).scalar_one_or_none()


def list_media(
    db: Session,
    mime_type: str | None = None,
) -> list[Media]:
    stmt = select(Media).order_by(Media.created_at.desc())

    if mime_type is not None:
        stmt = stmt.where(Media.mime_type == mime_type)

    return db.execute(stmt).scalars().all()


def create_media(
    db: Session,
    original_filename: str,
    stored_filename: str,
    storage_path: str,
    mime_type: str,
    size_bytes: int = 0,
    url: str | None = None,
    title: str | None = None,
    alt_text: str | None = None,
    description: str | None = None,
    uploaded_by: int | None = None,
) -> Media:
    media = Media(
        original_filename=original_filename,
        stored_filename=stored_filename,
        storage_path=storage_path,
        url=url,
        mime_type=mime_type,
        size_bytes=size_bytes,
        title=title,
        alt_text=alt_text,
        description=description,
        uploaded_by=uploaded_by,
    )

    db.add(media)
    db.commit()
    db.refresh(media)

    return media


def update_media(
    db: Session,
    media_id: int,
    *,
    title: str | None = None,
    alt_text: str | None = None,
    description: str | None = None,
    url: str | None = None,
) -> Media | None:
    media = get_media(
        db=db,
        media_id=media_id,
    )

    if media is None:
        return None

    if title is not None:
        media.title = title

    if alt_text is not None:
        media.alt_text = alt_text

    if description is not None:
        media.description = description

    if url is not None:
        media.url = url

    db.commit()
    db.refresh(media)

    return media


def delete_media(
    db: Session,
    media_id: int,
) -> bool:
    media = get_media(
        db=db,
        media_id=media_id,
    )

    if media is None:
        return False

    # Primero eliminamos el objeto físico.
    delete_object(media.storage_path)

    # Si MinIO tuvo éxito, eliminamos el registro.
    db.delete(media)
    db.commit()

    return True
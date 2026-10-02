from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.tag import Tag
from app.schemas.tag import TagCreate, TagUpdate


def get_tag(
    db: Session,
    tag_id: int,
) -> Tag | None:

    return db.execute(
        select(Tag).where(
            Tag.id == tag_id
        )
    ).scalar_one_or_none()


def get_tag_by_slug(
    db: Session,
    slug: str,
) -> Tag | None:

    return db.execute(
        select(Tag).where(
            Tag.slug == slug
        )
    ).scalar_one_or_none()


def list_tags(
    db: Session,
):

    stmt = select(Tag).order_by(
        Tag.name.asc()
    )

    return db.execute(
        stmt
    ).scalars().all()


def create_tag(
    db: Session,
    data: TagCreate,
) -> Tag:

    tag = Tag(
        name=data.name,
        slug=data.slug,
    )

    db.add(tag)
    db.commit()
    db.refresh(tag)

    return tag


def update_tag(
    db: Session,
    tag_id: int,
    data: TagUpdate,
) -> Tag | None:

    tag = get_tag(
        db,
        tag_id,
    )

    if tag is None:
        return None

    update_data = data.model_dump(
        exclude_unset=True,
    )

    for field, value in update_data.items():
        setattr(
            tag,
            field,
            value,
        )

    db.commit()
    db.refresh(tag)

    return tag


def delete_tag(
    db: Session,
    tag_id: int,
) -> bool:

    tag = get_tag(
        db,
        tag_id,
    )

    if tag is None:
        return False

    db.delete(tag)
    db.commit()

    return True

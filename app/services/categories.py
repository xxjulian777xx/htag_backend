from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


def get_category(
    db: Session,
    category_id: int,
) -> Category | None:

    return db.execute(
        select(Category).where(
            Category.id == category_id
        )
    ).scalar_one_or_none()


def get_category_by_slug(
    db: Session,
    slug: str,
) -> Category | None:

    return db.execute(
        select(Category).where(
            Category.slug == slug
        )
    ).scalar_one_or_none()


def list_categories(
    db: Session,
    active_only: bool = False,
):

    stmt = select(Category).order_by(
        Category.sort_order.asc(),
        Category.name.asc(),
    )

    if active_only:
        stmt = stmt.where(
            Category.is_active.is_(True)
        )

    return db.execute(
        stmt
    ).scalars().all()


def create_category(
    db: Session,
    data: CategoryCreate,
) -> Category:

    category = Category(
        name=data.name,
        slug=data.slug,
        description=data.description,
        parent_id=data.parent_id,
        is_active=data.is_active,
        sort_order=data.sort_order,
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    return category


def update_category(
    db: Session,
    category_id: int,
    data: CategoryUpdate,
) -> Category | None:

    category = get_category(
        db,
        category_id,
    )

    if category is None:
        return None

    update_data = data.model_dump(
        exclude_unset=True,
    )

    for field, value in update_data.items():
        setattr(
            category,
            field,
            value,
        )

    db.commit()
    db.refresh(category)

    return category


def delete_category(
    db: Session,
    category_id: int,
) -> bool:

    category = get_category(
        db,
        category_id,
    )

    if category is None:
        return False

    db.delete(category)
    db.commit()

    return True
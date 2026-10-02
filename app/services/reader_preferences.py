from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.reader_preference import ReaderPreference
from app.schemas.reader_preference import ReaderPreferenceUpdate


DEFAULT_FONT_SIZE = "medium"
DEFAULT_THEME = "system"
DEFAULT_VOICE_ENABLED = False


def get_reader_preferences(
    db: Session,
    user_id: int,
) -> ReaderPreference:

    preference = db.execute(
        select(ReaderPreference).where(
            ReaderPreference.user_id == user_id
        )
    ).scalar_one_or_none()

    if preference is not None:
        return preference

    preference = ReaderPreference(
        user_id=user_id,
        font_size=DEFAULT_FONT_SIZE,
        theme=DEFAULT_THEME,
        voice_enabled=DEFAULT_VOICE_ENABLED,
    )

    db.add(preference)
    db.commit()
    db.refresh(preference)

    return preference


def update_reader_preferences(
    db: Session,
    user_id: int,
    data: ReaderPreferenceUpdate,
) -> ReaderPreference:

    preference = db.execute(
        select(ReaderPreference).where(
            ReaderPreference.user_id == user_id
        )
    ).scalar_one_or_none()

    if preference is None:
        preference = ReaderPreference(
            user_id=user_id,
            font_size=DEFAULT_FONT_SIZE,
            theme=DEFAULT_THEME,
            voice_enabled=DEFAULT_VOICE_ENABLED,
        )

        db.add(preference)
        db.flush()

    update_data = data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(
            preference,
            field,
            value,
        )

    db.commit()
    db.refresh(preference)

    return preference
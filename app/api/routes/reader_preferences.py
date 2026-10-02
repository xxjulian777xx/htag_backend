from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.reader_preference import (
    ReaderPreferenceResponse,
    ReaderPreferenceUpdate,
)
from app.services.reader_preferences import (
    get_reader_preferences,
    update_reader_preferences,
)


router = APIRouter(
    prefix="/v1/reader/preferences",
    tags=["Reader Preferences"],
)


@router.get(
    "",
    response_model=ReaderPreferenceResponse,
)
def get_preferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_reader_preferences(
        db=db,
        user_id=current_user.id,
    )


@router.put(
    "",
    response_model=ReaderPreferenceResponse,
)
def update_preferences(
    data: ReaderPreferenceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_reader_preferences(
        db=db,
        user_id=current_user.id,
        data=data,
    )
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class MediaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    original_filename: str
    stored_filename: str
    storage_path: str
    url: str | None
    mime_type: str
    size_bytes: int
    title: str | None
    alt_text: str | None
    description: str | None
    uploaded_by: int | None
    created_at: datetime
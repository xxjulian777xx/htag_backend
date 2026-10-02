from datetime import datetime

from pydantic import BaseModel, ConfigDict


class OCRProcessRequest(BaseModel):
    media_id: int
    language: str = "spa+eng"


class OCRResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    media_id: int
    status: str
    extracted_text: str | None
    error_message: str | None
    processed_by: int | None
    created_at: datetime
    processed_at: datetime | None
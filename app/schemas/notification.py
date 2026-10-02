from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class NotificationCreate(BaseModel):
    user_id: int = Field(..., gt=0)
    notification_type: str = Field(
        ...,
        min_length=1,
        max_length=50,
    )
    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
    )
    message: str = Field(
        ...,
        min_length=1,
    )
    data: dict | None = None


class NotificationResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    user_id: int
    notification_type: str
    title: str
    message: str
    data: dict | None
    is_read: bool
    created_at: datetime
    read_at: datetime | None
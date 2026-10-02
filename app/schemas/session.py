from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SessionResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )
    id: int
    user_id: int
    device_name: str | None
    created_at: datetime
    last_activity_at: datetime
    expires_at: datetime
    revoked_at: datetime | None


class SessionListResponse(BaseModel):
    items: list[SessionResponse]
    page: int
    page_size: int
    total: int
    pages: int
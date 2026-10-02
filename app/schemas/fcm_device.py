from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class FCMDeviceRegister(BaseModel):
    fcm_token: str = Field(
        ...,
        min_length=1,
        max_length=1000,
    )

    platform: str = Field(
        default="unknown",
        min_length=1,
        max_length=30,
    )

    device_name: str | None = Field(
        default=None,
        max_length=255,
    )


class FCMDeviceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    fcm_token: str
    platform: str
    device_name: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


FontSize = Literal[
    "small",
    "medium",
    "large",
    "xlarge",
]

Theme = Literal[
    "light",
    "dark",
    "system",
]


class ReaderPreferenceResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    user_id: int
    font_size: FontSize
    theme: Theme
    voice_enabled: bool
    created_at: datetime
    updated_at: datetime


class ReaderPreferenceUpdate(BaseModel):
    font_size: FontSize | None = None
    theme: Theme | None = None
    voice_enabled: bool | None = None
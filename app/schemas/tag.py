from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TagBase(BaseModel):
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )

    slug: str = Field(
        ...,
        min_length=1,
        max_length=120,
    )


class TagCreate(TagBase):
    pass


class TagUpdate(BaseModel):
    name: str | None = Field(
        None,
        min_length=1,
        max_length=100,
    )

    slug: str | None = Field(
        None,
        min_length=1,
        max_length=120,
    )


class TagResponse(TagBase):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    created_at: datetime

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ReaderCategoryResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    name: str
    slug: str


class ReaderTagResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    name: str
    slug: str


class ReaderMediaResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )

    id: int
    url: str | None
    title: str | None
    alt_text: str | None
    description: str | None
    mime_type: str


class ReaderBlockResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    block_type: str
    position: int
    data: dict = Field(
        default_factory=dict,
    )


class ReaderArticleSummaryResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )

    id: int
    title: str
    slug: str
    excerpt: str | None
    published_at: datetime | None

    category: ReaderCategoryResponse | None

    cover: ReaderMediaResponse | None = Field(
        default=None,
        validation_alias="cover_media",
        serialization_alias="cover",
    )

    tags: list[ReaderTagResponse] = Field(
        default_factory=list,
    )


class ReaderArticleResponse(
    ReaderArticleSummaryResponse
):
    blocks: list[ReaderBlockResponse] = Field(
        default_factory=list,
    )


class ReaderArticleListResponse(BaseModel):
    items: list[ReaderArticleSummaryResponse] = Field(
        default_factory=list,
    )

    total: int
    page: int
    page_size: int
    pages: int
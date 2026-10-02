from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ArticleBlockBase(BaseModel):
    block_type: str = Field(..., min_length=1, max_length=50)
    position: int = Field(default=0, ge=0)
    data: dict = Field(default_factory=dict)


class ArticleBlockCreate(ArticleBlockBase):
    pass


class ArticleBlockUpdate(BaseModel):
    block_type: str | None = Field(None, min_length=1, max_length=50)
    position: int | None = Field(None, ge=0)
    data: dict | None = None


class ArticleBlockResponse(ArticleBlockBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    article_id: int
    created_at: datetime
    updated_at: datetime


class ArticleTagResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    created_at: datetime


ArticleStatus = Literal["draft", "scheduled", "published", "archived"]


class ArticleBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=300)
    slug: str = Field(..., min_length=1, max_length=350)
    excerpt: str | None = None
    status: ArticleStatus = "draft"
    author_id: int | None = None
    category_id: int | None = None
    cover_media_id: int | None = None
    scheduled_at: datetime | None = None
    published_at: datetime | None = None
    is_featured: bool = False
    allow_comments: bool = True
    seo_title: str | None = Field(None, max_length=300)
    seo_description: str | None = Field(None, max_length=500)


class ArticleCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=300)
    slug: str = Field(..., min_length=1, max_length=350)
    excerpt: str | None = None
    author_id: int | None = None
    category_id: int | None = None
    cover_media_id: int | None = None
    is_featured: bool = False
    allow_comments: bool = True
    seo_title: str | None = Field(None, max_length=300)
    seo_description: str | None = Field(None, max_length=500)

    blocks: list[ArticleBlockCreate] = Field(default_factory=list)
    tag_ids: list[int] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_blocks(self):
        positions = [block.position for block in self.blocks]

        if len(positions) != len(set(positions)):
            raise ValueError("Article block positions must be unique")

        return self


class ArticleUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=300)
    slug: str | None = Field(None, min_length=1, max_length=350)
    excerpt: str | None = None
    author_id: int | None = None
    category_id: int | None = None
    cover_media_id: int | None = None
    is_featured: bool | None = None
    allow_comments: bool | None = None
    seo_title: str | None = Field(None, max_length=300)
    seo_description: str | None = Field(None, max_length=500)

    blocks: list[ArticleBlockCreate] | None = None
    tag_ids: list[int] | None = None

    @model_validator(mode="after")
    def validate_blocks(self):
        if self.blocks is not None:
            positions = [block.position for block in self.blocks]

            if len(positions) != len(set(positions)):
                raise ValueError("Article block positions must be unique")

        return self


class ArticleSchedule(BaseModel):
    scheduled_at: datetime


class ArticlePublish(BaseModel):
    published_at: datetime | None = None


class ArticleResponse(ArticleBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime

    blocks: list[ArticleBlockResponse] = Field(default_factory=list)
    tags: list[ArticleTagResponse] = Field(default_factory=list)

class ArticleArchive(BaseModel):
    pass
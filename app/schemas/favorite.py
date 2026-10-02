from datetime import datetime

from pydantic import BaseModel, ConfigDict


class FavoriteArticleResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    title: str
    slug: str
    excerpt: str | None
    status: str
    category_id: int | None
    cover_media_id: int | None
    published_at: datetime | None


class FavoriteResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    article_id: int
    created_at: datetime
    article: FavoriteArticleResponse
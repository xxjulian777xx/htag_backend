from pydantic import BaseModel, Field

from app.schemas.article import ArticleResponse


class ArticleListResponse(BaseModel):
    items: list[ArticleResponse] = Field(
        default_factory=list,
    )

    total: int

    page: int

    page_size: int

    pages: int
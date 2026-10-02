from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ArticleHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    article_id: int
    user_id: int | None
    actor_type: str
    action: str
    from_status: str | None
    to_status: str | None
    created_at: datetime
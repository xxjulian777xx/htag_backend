from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    slug: str = Field(..., min_length=1, max_length=180)
    description: str | None = None
    parent_id: int | None = None
    is_active: bool = True
    sort_order: int = 0


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=150)
    slug: str | None = Field(None, min_length=1, max_length=180)
    description: str | None = None
    parent_id: int | None = None
    is_active: bool | None = None
    sort_order: int | None = None


class CategoryResponse(CategoryBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
)


class UserListItem(BaseModel):

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    username: str
    email: EmailStr
    is_active: bool


class UserListResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True,
    )

    items: list[UserListItem]
    page: int
    page_size: int
    total: int
    pages: int


class UserCreate(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=100,
    )

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=128,
    )

    role: str = Field(
        min_length=1,
        max_length=100,
    )


class UserUpdate(BaseModel):
    email: EmailStr | None = None

    is_active: bool | None = None

    role: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )


class ResetPasswordRequest(BaseModel):
    new_password: str = Field(
        min_length=8,
        max_length=128,
    )
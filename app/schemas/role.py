from pydantic import BaseModel, Field


class PermissionResponse(BaseModel):
    id: int
    name: str
    description: str | None


class RoleResponse(BaseModel):
    id: int
    name: str
    description: str | None
    permissions: list[PermissionResponse]


class RoleCreate(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=100,
    )

    description: str | None = Field(
        default=None,
        max_length=500,
    )


class RolePermissionsUpdate(BaseModel):
    permission_ids: list[int] = Field(
        min_length=0,
    )


class RoleUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    description: str | None = Field(
        default=None,
        max_length=500,
    )
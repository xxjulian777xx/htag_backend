from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import require_permission
from app.core.database import get_db
from app.models.permission import Permission
from app.models.role import Role
from app.models.user import User
from app.schemas.role import (
    RoleCreate,
    RolePermissionsUpdate,
    RoleResponse,
    RoleUpdate,
)


router = APIRouter(
    prefix="/v1/roles",
    tags=["Roles"],
)


@router.get(
    "",
    response_model=list[RoleResponse],
)
def list_roles(
    current_user: User = Depends(
        require_permission("roles.read")
    ),
    db: Session = Depends(get_db),
):
    stmt = (
        select(Role)
        .order_by(Role.id)
    )

    roles = db.scalars(stmt).all()

    return roles


@router.post(
    "",
    response_model=RoleResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_role(
    data: RoleCreate,
    current_user: User = Depends(
        require_permission("roles.manage")
    ),
    db: Session = Depends(get_db),
):
    existing_role = db.scalar(
        select(Role).where(
            Role.name == data.name
        )
    )

    if existing_role is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El rol ya existe",
        )

    role = Role(
        name=data.name,
        description=data.description,
    )

    db.add(role)
    db.commit()
    db.refresh(role)

    return role


@router.put(
    "/{role_id}",
    response_model=RoleResponse,
)
def update_role(
    role_id: int,
    data: RoleUpdate,
    current_user: User = Depends(
        require_permission("roles.manage")
    ),
    db: Session = Depends(get_db),
):
    role = db.scalar(
        select(Role).where(
            Role.id == role_id
        )
    )

    if role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El rol no existe",
        )

    # ---------------------------------------------------------
    # PROTEGER ROL ADMINISTRADOR
    # ---------------------------------------------------------

    if role.name == "administrador":

        if data.name is not None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="El rol administrador principal no puede cambiar de nombre",
            )

    if data.name is not None:

        existing_role = db.scalar(
            select(Role).where(
                Role.name == data.name,
                Role.id != role_id,
            )
        )

        if existing_role is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El nombre del rol ya existe",
            )

        role.name = data.name

    if data.description is not None:
        role.description = data.description

    db.commit()
    db.refresh(role)

    return role


@router.put(
    "/{role_id}/permissions",
    response_model=RoleResponse,
)
def update_role_permissions(
    role_id: int,
    data: RolePermissionsUpdate,
    current_user: User = Depends(
        require_permission("roles.manage")
    ),
    db: Session = Depends(get_db),
):
    role = db.scalar(
        select(Role).where(
            Role.id == role_id
        )
    )

    if role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El rol no existe",
        )

    # ---------------------------------------------------------
    # PROTEGER PERMISOS DEL ROL ADMINISTRADOR
    # ---------------------------------------------------------

    if role.name == "administrador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El rol administrador principal no puede modificar sus permisos",
        )

    permissions = []

    if data.permission_ids:

        stmt = select(Permission).where(
            Permission.id.in_(data.permission_ids)
        )

        permissions = db.scalars(stmt).all()

        found_ids = {
            permission.id
            for permission in permissions
        }

        requested_ids = set(
            data.permission_ids
        )

        missing_ids = requested_ids - found_ids

        if missing_ids:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Permisos no encontrados: {sorted(missing_ids)}",
            )

    role.permissions = permissions

    db.commit()
    db.refresh(role)

    return role


@router.delete(
    "/{role_id}",
)
def delete_role(
    role_id: int,
    current_user: User = Depends(
        require_permission("roles.manage")
    ),
    db: Session = Depends(get_db),
):
    role = db.scalar(
        select(Role).where(
            Role.id == role_id
        )
    )

    if role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El rol no existe",
        )

    # ---------------------------------------------------------
    # PROTEGER ROL ADMINISTRADOR
    # ---------------------------------------------------------

    if role.name == "administrador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El rol administrador principal no puede eliminarse",
        )

    # ---------------------------------------------------------
    # NO PERMITIR ELIMINAR ROLES CON USUARIOS ASIGNADOS
    # ---------------------------------------------------------

    if role.users:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se puede eliminar un rol que tiene usuarios asignados",
        )

    db.delete(role)
    db.commit()

    return {
        "message": "Rol eliminado correctamente",
        "role_id": role_id,
    }
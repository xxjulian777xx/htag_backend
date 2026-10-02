from datetime import (
    datetime,
    timedelta,
    timezone,
)

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.dependencies import require_permission
from app.core.database import get_db
from app.core.security import hash_password
from app.models.role import Role
from app.models.session import Session as UserSession
from app.models.user import User
from app.schemas.session import (
    SessionListResponse,
    SessionResponse,
)
from app.schemas.user import (
    ResetPasswordRequest,
    UserCreate,
    UserListItem,
    UserListResponse,
    UserUpdate,
)
from app.services.auth import (
    AuthenticationError,
    reset_user_password,
)

from math import ceil

router = APIRouter(
    prefix="/v1/users",
    tags=["Users"],
)

@router.get(
    "",
    response_model=UserListResponse,
)
def list_users(
    search: str | None = None,
    user_status: str = "all",
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(
        require_permission("users.read")
    ),
    db: Session = Depends(get_db),
):
    # ---------------------------------------------------------
    # VALIDAR PAGINACIÓN
    # ---------------------------------------------------------

    if page < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "El número de página debe ser "
                "mayor o igual a 1"
            ),
        )

    if page_size < 1 or page_size > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "El tamaño de página debe estar "
                "entre 1 y 100"
            ),
        )

    # ---------------------------------------------------------
    # VALIDAR FILTRO DE ESTADO
    # ---------------------------------------------------------

    allowed_statuses = {
        "active",
        "inactive",
        "all",
    }

    if user_status not in allowed_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "El estado debe ser: "
                "active, inactive o all"
            ),
        )

    # ---------------------------------------------------------
    # CONSTRUCCIÓN DE FILTROS
    # ---------------------------------------------------------

    filters = []

    # ---------------------------------------------------------
    # BÚSQUEDA
    # ---------------------------------------------------------

    if search is not None:

        search = search.strip()

        if search:
            search_pattern = f"%{search}%"

            filters.append(
                (
                    User.username.ilike(
                        search_pattern
                    )
                    |
                    User.email.ilike(
                        search_pattern
                    )
                )
            )

    # ---------------------------------------------------------
    # FILTRO DE ESTADO
    # ---------------------------------------------------------

    if user_status == "active":

        filters.append(
            User.is_active.is_(True)
        )

    elif user_status == "inactive":

        filters.append(
            User.is_active.is_(False)
        )

    # ---------------------------------------------------------
    # TOTAL
    # ---------------------------------------------------------

    total_stmt = (
        select(func.count())
        .select_from(User)
        .where(*filters)
    )

    total = db.scalar(total_stmt) or 0

    # ---------------------------------------------------------
    # PAGINACIÓN
    # ---------------------------------------------------------

    offset = (page - 1) * page_size

    stmt = (
        select(User)
        .where(*filters)
        .order_by(User.id)
        .offset(offset)
        .limit(page_size)
    )

    users = db.scalars(stmt).all()

    # ---------------------------------------------------------
    # TOTAL DE PÁGINAS
    # ---------------------------------------------------------

    pages = (
        ceil(total / page_size)
        if total > 0
        else 0
    )

    # ---------------------------------------------------------
    # RESPUESTA
    # ---------------------------------------------------------

    return UserListResponse(
        items=users,
        page=page,
        page_size=page_size,
        total=total,
        pages=pages,
    )


@router.post(
    "",
    response_model=UserListItem,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    data: UserCreate,
    current_user: User = Depends(
        require_permission("users.create")
    ),
    db: Session = Depends(get_db),
):
    existing_username = db.scalar(
        select(User).where(
            User.username == data.username
        )
    )

    if existing_username is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El username ya existe",
        )

    existing_email = db.scalar(
        select(User).where(
            User.email == data.email
        )
    )

    if existing_email is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El email ya existe",
        )

    role = db.scalar(
        select(Role).where(
            Role.name == data.role
        )
    )

    if role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El rol no existe",
        )

    user = User(
        username=data.username,
        email=data.email,
        password_hash=hash_password(data.password),
        is_active=True,
        token_version=1,
    )

    user.roles.append(role)

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@router.put(
    "/{user_id}",
    response_model=UserListItem,
)
def update_user(
    user_id: int,
    data: UserUpdate,
    current_user: User = Depends(
        require_permission("users.update")
    ),
    db: Session = Depends(get_db),
):
    user = db.scalar(
        select(User).where(
            User.id == user_id
        )
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )
        # ---------------------------------------------------------
    # PROTEGER CUENTA ADMINISTRADORA PRINCIPAL
    # ---------------------------------------------------------

    if user.id == 1:

        if data.role is not None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="La cuenta administradora principal no puede cambiar de rol",
            )

        if data.is_active is not None and not data.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="La cuenta administradora principal no puede ser desactivada",
            )
    # ---------------------------------------------------------
    # VALIDAR PERMISOS ANTES DE MODIFICAR DATOS
    # ---------------------------------------------------------

    if data.is_active is not None:

        has_disable_permission = any(
            permission.name == "users.disable"
            for role in current_user.roles
            for permission in role.permissions
        )

        if not has_disable_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para activar o desactivar usuarios",
            )

    # ---------------------------------------------------------
    # EMAIL
    # ---------------------------------------------------------

    if data.email is not None:

        existing_email = db.scalar(
            select(User).where(
                User.email == data.email,
                User.id != user_id,
            )
        )

        if existing_email is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El email ya existe",
            )

        user.email = data.email

    # ---------------------------------------------------------
    # ROL
    # ---------------------------------------------------------

    if data.role is not None:

        role = db.scalar(
            select(Role).where(
                Role.name == data.role
            )
        )

        if role is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El rol no existe",
            )

        user.roles = [role]

    # ---------------------------------------------------------
    # ESTADO
    # ---------------------------------------------------------

    if data.is_active is not None:

        if user.is_active and not data.is_active:

            now = datetime.now(timezone.utc)

            stmt = select(UserSession).where(
                UserSession.user_id == user.id,
                UserSession.revoked_at.is_(None),
            )

            sessions = db.scalars(stmt).all()

            for user_session in sessions:
                user_session.revoked_at = now

            user.token_version += 1

        user.is_active = data.is_active

    db.commit()
    db.refresh(user)

    return user

@router.get(
    "/{user_id}/sessions",
    response_model=SessionListResponse,
)
def list_user_sessions(
    user_id: int,
    session_status: str = "active",
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(
        require_permission("users.sessions.revoke")
    ),
    db: Session = Depends(get_db),
):
    user = db.scalar(
        select(User).where(
            User.id == user_id
        )
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )

    # ---------------------------------------------------------
    # VALIDAR PAGINACIÓN
    # ---------------------------------------------------------

    if page < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El número de página debe ser mayor o igual a 1",
        )

    if page_size < 1 or page_size > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El tamaño de página debe estar entre 1 y 100",
        )

    # ---------------------------------------------------------
    # VALIDAR FILTRO DE ESTADO
    # ---------------------------------------------------------

    allowed_statuses = {
        "active",
        "revoked",
        "all",
    }

    if session_status not in allowed_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "El estado debe ser: "
                "active, revoked o all"
            ),
        )

    # ---------------------------------------------------------
    # FECHA ACTUAL
    # ---------------------------------------------------------

    now = datetime.now(timezone.utc)

    # ---------------------------------------------------------
    # CONSTRUCCIÓN DE FILTROS
    # ---------------------------------------------------------

    filters = [
        UserSession.user_id == user_id
    ]

    if session_status == "active":

        filters.extend(
            [
                UserSession.revoked_at.is_(None),
                UserSession.expires_at > now,
            ]
        )

    elif session_status == "revoked":

        filters.append(
            UserSession.revoked_at.is_not(None)
        )

    # ---------------------------------------------------------
    # TOTAL
    # ---------------------------------------------------------

    total_stmt = (
        select(func.count())
        .select_from(UserSession)
        .where(*filters)
    )

    total = db.scalar(total_stmt) or 0

    # ---------------------------------------------------------
    # PAGINACIÓN
    # ---------------------------------------------------------

    offset = (page - 1) * page_size

    stmt = (
        select(UserSession)
        .where(*filters)
        .order_by(
            UserSession.created_at.desc()
        )
        .offset(offset)
        .limit(page_size)
    )

    sessions = db.scalars(stmt).all()

    # ---------------------------------------------------------
    # TOTAL DE PÁGINAS
    # ---------------------------------------------------------

    pages = (
        ceil(total / page_size)
        if total > 0
        else 0
    )

    return SessionListResponse(
        items=sessions,
        page=page,
        page_size=page_size,
        total=total,
        pages=pages,
    )

@router.delete(
    "/{user_id}/sessions/{session_id}",
)
def revoke_user_session(
    user_id: int,
    session_id: int,
    current_user: User = Depends(
        require_permission("users.sessions.revoke")
    ),
    db: Session = Depends(get_db),
):
    user = db.scalar(
        select(User).where(
            User.id == user_id
        )
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )

    user_session = db.scalar(
        select(UserSession).where(
            UserSession.id == session_id,
            UserSession.user_id == user_id,
        )
    )

    if user_session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sesión no encontrada",
        )

    if user_session.revoked_at is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="La sesión ya fue revocada",
        )

    user_session.revoked_at = datetime.now(timezone.utc)

    db.commit()

    return {
        "message": "Sesión revocada correctamente",
        "session_id": user_session.id,
    }



@router.post(
    "/{user_id}/sessions/cleanup",
)
def cleanup_user_sessions(
    user_id: int,
    current_user: User = Depends(
        require_permission("users.sessions.revoke")
    ),
    db: Session = Depends(get_db),
):
    user = db.scalar(
        select(User).where(
            User.id == user_id
        )
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )

    # ---------------------------------------------------------
    # FECHA DE CORTE
    # ---------------------------------------------------------

    now = datetime.now(timezone.utc)

    #from datetime import timedelta

    cutoff = now - timedelta(days=30)

    # ---------------------------------------------------------
    # BUSCAR SESIONES PARA ELIMINAR
    # ---------------------------------------------------------

    stmt = select(UserSession).where(
        UserSession.user_id == user_id,
        UserSession.expires_at < cutoff,
    )

    sessions = db.scalars(stmt).all()

    deleted_count = len(sessions)

    for user_session in sessions:
        db.delete(user_session)

    db.commit()

    return {
        "message": "Limpieza de sesiones completada",
        "user_id": user_id,
        "deleted_sessions": deleted_count,
    }


@router.post(
    "/{user_id}/password",
)
def reset_password(
    user_id: int,
    request: ResetPasswordRequest,
    current_user: User = Depends(
        require_permission("users.password.reset")
    ),
    db: Session = Depends(get_db),
):

    user = db.scalar(
        select(User).where(
            User.id == user_id
        )
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )

    try:

        reset_user_password(
            db=db,
            user=user,
            new_password=request.new_password,
        )

        return {
            "message": "Contraseña restablecida correctamente",
            "user_id": user.id,
        }

    except AuthenticationError as exc:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
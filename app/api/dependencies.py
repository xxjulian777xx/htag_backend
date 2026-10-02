from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_token
from app.models.user import User


security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:

    token = credentials.credentials

    try:
        payload = decode_token(token)

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El token no es un access token",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    user_id = payload.get("sub")
    token_version = payload.get("token_version")

    if not user_id or token_version is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    try:
        user_id = int(user_id)
        token_version = int(token_version)

    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    stmt = select(User).where(
        User.id == user_id
    )

    user = db.scalar(stmt)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario desactivado",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    if user.token_version != token_version:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token revocado",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    return user


def require_permission(permission_name: str):

    def permission_dependency(
        current_user: User = Depends(get_current_user),
    ) -> User:

        has_permission = any(
            permission.name == permission_name
            for role in current_user.roles
            for permission in role.permissions
        )

        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para realizar esta acción",
            )

        return current_user

    return permission_dependency
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)
from app.models.session import Session as UserSession
from app.models.user import User


class AuthenticationError(Exception):
    pass


def authenticate_user(
    db: Session,
    username: str,
    password: str,
) -> User:

    stmt = select(User).where(
        User.username == username
    )

    user = db.scalar(stmt)

    if user is None:
        raise AuthenticationError(
            "Usuario o contraseña incorrectos"
        )

    if not user.is_active:
        raise AuthenticationError(
            "El usuario está desactivado"
        )

    if not verify_password(
        password,
        user.password_hash,
    ):
        raise AuthenticationError(
            "Usuario o contraseña incorrectos"
        )

    return user


def create_user_session(
    db: Session,
    user: User,
    device_name: str | None = None,
) -> tuple[str, str]:

    now = datetime.now(timezone.utc)

    expires_at = now + timedelta(
        days=settings.refresh_token_expire_days
    )

    user_session = UserSession(
        user_id=user.id,
        refresh_token_hash="",
        token_version=user.token_version,
        device_name=device_name,
        created_at=now,
        last_activity_at=now,
        expires_at=expires_at,
    )

    db.add(user_session)
    db.flush()

    access_token = create_access_token(
        user_id=user.id,
        token_version=user.token_version,
    )

    refresh_token = create_refresh_token(
        user_id=user.id,
        token_version=user.token_version,
        session_id=user_session.id,
    )

    user_session.refresh_token_hash = hash_refresh_token(
        refresh_token
    )

    db.commit()

    return access_token, refresh_token


def refresh_user_session(
    db: Session,
    refresh_token: str,
) -> tuple[str, str]:

    try:
        payload = decode_token(refresh_token)

    except Exception:
        raise AuthenticationError(
            "Refresh token inválido o expirado"
        )

    if payload.get("type") != "refresh":
        raise AuthenticationError(
            "El token no es un refresh token"
        )

    user_id = payload.get("sub")
    session_id = payload.get("session_id")
    token_version = payload.get("token_version")

    if not user_id or not session_id or token_version is None:
        raise AuthenticationError(
            "Refresh token inválido"
        )

    stmt = select(User).where(
        User.id == int(user_id)
    )

    user = db.scalar(stmt)

    if user is None:
        raise AuthenticationError(
            "Usuario no encontrado"
        )

    if not user.is_active:
        raise AuthenticationError(
            "El usuario está desactivado"
        )

    if user.token_version != int(token_version):
        raise AuthenticationError(
            "El refresh token ya no es válido"
        )

    session_stmt = select(UserSession).where(
        UserSession.id == int(session_id),
        UserSession.user_id == user.id,
    )

    user_session = db.scalar(session_stmt)

    if user_session is None:
        raise AuthenticationError(
            "Sesión no encontrada"
        )

    if user_session.revoked_at is not None:
        raise AuthenticationError(
            "La sesión fue revocada"
        )

    now = datetime.now(timezone.utc)

    if user_session.expires_at.replace(
        tzinfo=timezone.utc
    ) <= now:

        raise AuthenticationError(
            "La sesión ha expirado"
        )

    token_hash = hash_refresh_token(
        refresh_token
    )

    if token_hash != user_session.refresh_token_hash:
        raise AuthenticationError(
            "Refresh token inválido"
        )

    new_access_token = create_access_token(
        user_id=user.id,
        token_version=user.token_version,
    )

    new_refresh_token = create_refresh_token(
        user_id=user.id,
        token_version=user.token_version,
        session_id=user_session.id,
    )

    user_session.refresh_token_hash = hash_refresh_token(
        new_refresh_token
    )

    user_session.last_activity_at = now

    db.commit()

    return new_access_token, new_refresh_token


def logout_user_session(
    db: Session,
    refresh_token: str,
) -> None:

    try:
        payload = decode_token(refresh_token)

    except Exception:
        raise AuthenticationError(
            "Refresh token inválido o expirado"
        )

    if payload.get("type") != "refresh":
        raise AuthenticationError(
            "El token no es un refresh token"
        )

    user_id = payload.get("sub")
    session_id = payload.get("session_id")
    token_version = payload.get("token_version")

    if not user_id or not session_id or token_version is None:
        raise AuthenticationError(
            "Refresh token inválido"
        )

    stmt = select(UserSession).where(
        UserSession.id == int(session_id),
        UserSession.user_id == int(user_id),
    )

    user_session = db.scalar(stmt)

    if user_session is None:
        raise AuthenticationError(
            "Sesión no encontrada"
        )

    if user_session.revoked_at is not None:
        return

    if user_session.token_version != int(token_version):
        raise AuthenticationError(
            "La sesión ya no es válida"
        )

    token_hash = hash_refresh_token(
        refresh_token
    )

    if token_hash != user_session.refresh_token_hash:
        raise AuthenticationError(
            "Refresh token inválido"
        )

    user_session.revoked_at = datetime.now(timezone.utc)

    db.commit()


def revoke_all_user_sessions(
    db: Session,
    user: User,
) -> None:

    now = datetime.now(timezone.utc)

    stmt = select(UserSession).where(
        UserSession.user_id == user.id,
        UserSession.revoked_at.is_(None),
    )

    sessions = db.scalars(stmt).all()

    for user_session in sessions:
        user_session.revoked_at = now


def logout_all_user_sessions(
    db: Session,
    user: User,
) -> None:

    revoke_all_user_sessions(
        db=db,
        user=user,
    )

    user.token_version += 1

    db.commit()


def change_user_password(
    db: Session,
    user: User,
    current_password: str,
    new_password: str,
) -> None:

    if not verify_password(
        current_password,
        user.password_hash,
    ):
        raise AuthenticationError(
            "La contraseña actual es incorrecta"
        )

    if verify_password(
        new_password,
        user.password_hash,
    ):
        raise AuthenticationError(
            "La nueva contraseña debe ser diferente a la actual"
        )

    user.password_hash = hash_password(
        new_password
    )

    revoke_all_user_sessions(
        db=db,
        user=user,
    )

    user.token_version += 1

    db.commit()


def reset_user_password(
    db: Session,
    user: User,
    new_password: str,
) -> None:

    if verify_password(
        new_password,
        user.password_hash,
    ):
        raise AuthenticationError(
            "La nueva contraseña debe ser diferente a la actual"
        )

    user.password_hash = hash_password(
        new_password
    )

    revoke_all_user_sessions(
        db=db,
        user=user,
    )

    user.token_version += 1

    db.commit()
from datetime import datetime, timedelta, timezone
import hashlib

import jwt
from pwdlib import PasswordHash

from app.core.config import settings


# ============================================================
# PASSWORD HASHING
# ============================================================

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(
    password: str,
    hashed_password: str,
) -> bool:
    return password_hash.verify(
        password,
        hashed_password,
    )


# ============================================================
# REFRESH TOKEN HASH
# ============================================================

def hash_refresh_token(token: str) -> str:
    """
    Genera una huella SHA-256 del refresh token.

    Nunca almacenamos el refresh token original en PostgreSQL.
    """

    return hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()


# ============================================================
# JWT
# ============================================================

def create_access_token(
    user_id: int,
    token_version: int,
) -> str:

    now = datetime.now(timezone.utc)

    expires_at = now + timedelta(
        minutes=settings.access_token_expire_minutes
    )

    payload = {
        "sub": str(user_id),
        "type": "access",
        "token_version": token_version,
        "iat": now,
        "exp": expires_at,
    }

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def create_refresh_token(
    user_id: int,
    token_version: int,
    session_id: int,
) -> str:

    now = datetime.now(timezone.utc)

    expires_at = now + timedelta(
        days=settings.refresh_token_expire_days
    )

    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "token_version": token_version,
        "session_id": session_id,
        "iat": now,
        "exp": expires_at,
    }

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def decode_token(token: str) -> dict:
    return jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
    )
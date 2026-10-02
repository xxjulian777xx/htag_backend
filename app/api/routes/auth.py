from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import (
    get_current_user,
    require_permission,
)
from app.core.database import get_db
from app.models.user import User
from app.schemas.auth import (
    ChangePasswordRequest,
    LoginRequest,
    RefreshRequest,
    TokenResponse,
)
from app.services.auth import (
    AuthenticationError,
    authenticate_user,
    change_user_password,
    create_user_session,
    logout_all_user_sessions,
    logout_user_session,
    refresh_user_session,
)


router = APIRouter(
    prefix="/v1/auth",
    tags=["Authentication"],
)


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db),
):

    try:

        user = authenticate_user(
            db=db,
            username=request.username,
            password=request.password,
        )

        access_token, refresh_token = create_user_session(
            db=db,
            user=user,
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    except AuthenticationError as exc:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        )


@router.post(
    "/refresh",
    response_model=TokenResponse,
)
def refresh(
    request: RefreshRequest,
    db: Session = Depends(get_db),
):

    try:

        access_token, refresh_token = refresh_user_session(
            db=db,
            refresh_token=request.refresh_token,
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    except AuthenticationError as exc:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        )


@router.post(
    "/logout",
)
def logout(
    request: RefreshRequest,
    db: Session = Depends(get_db),
):

    try:

        logout_user_session(
            db=db,
            refresh_token=request.refresh_token,
        )

        return {
            "message": "Sesión cerrada correctamente"
        }

    except AuthenticationError as exc:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        )


@router.get(
    "/me",
)
def me(
    current_user: User = Depends(get_current_user),
):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "is_active": current_user.is_active,
        "roles": [
            {
                "id": role.id,
                "name": role.name,
                "description": role.description,
                "permissions": [
                    {
                        "id": permission.id,
                        "name": permission.name,
                        "description": permission.description,
                    }
                    for permission in role.permissions
                ],
            }
            for role in current_user.roles
        ],
    }


@router.post(
    "/logout-all",
)
def logout_all(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    logout_all_user_sessions(
        db=db,
        user=current_user,
    )

    return {
        "message": "Todas las sesiones fueron cerradas correctamente"
    }


@router.post(
    "/change-password",
)
def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    try:

        change_user_password(
            db=db,
            user=current_user,
            current_password=request.current_password,
            new_password=request.new_password,
        )

        return {
            "message": "Contraseña actualizada correctamente"
        }

    except AuthenticationError as exc:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.get(
    "/test-admin",
)
def test_admin_permission(
    current_user: User = Depends(
        require_permission("users.read")
    ),
):
    return {
        "message": "Permiso autorizado",
        "user": current_user.username,
        "permission": "users.read",
    }
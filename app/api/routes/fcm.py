from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.fcm_device import (
    FCMDeviceRegister,
    FCMDeviceResponse,
)
from app.services.fcm_devices import (
    deactivate_device,
    list_user_devices,
    register_device,
)

router = APIRouter(
    prefix="/v1/reader/devices",
    tags=["FCM Devices"],
)


@router.post(
    "",
    response_model=FCMDeviceResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_fcm_device(
    request: FCMDeviceRegister,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return register_device(
        db=db,
        user_id=current_user.id,
        fcm_token=request.fcm_token,
        platform=request.platform,
        device_name=request.device_name,
    )


@router.get(
    "",
    response_model=list[FCMDeviceResponse],
)
def get_my_fcm_devices(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return list_user_devices(
        db=db,
        user_id=current_user.id,
    )


@router.delete(
    "/{device_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_fcm_device(
    device_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    deleted = deactivate_device(
        db=db,
        user_id=current_user.id,
        device_id=device_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispositivo no encontrado",
        )

    return None
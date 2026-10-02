from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.fcm_device import FCMDevice


def get_device_by_token(
    db: Session,
    fcm_token: str,
) -> FCMDevice | None:
    stmt = select(FCMDevice).where(
        FCMDevice.fcm_token == fcm_token
    )

    return db.execute(stmt).scalar_one_or_none()


def register_device(
    db: Session,
    *,
    user_id: int,
    fcm_token: str,
    platform: str,
    device_name: str | None = None,
) -> FCMDevice:

    device = get_device_by_token(
        db=db,
        fcm_token=fcm_token,
    )

    if device is None:
        device = FCMDevice(
            user_id=user_id,
            fcm_token=fcm_token,
            platform=platform,
            device_name=device_name,
            is_active=True,
        )

        db.add(device)

    else:
        device.user_id = user_id
        device.platform = platform
        device.device_name = device_name
        device.is_active = True

    db.commit()
    db.refresh(device)

    return device


def list_user_devices(
    db: Session,
    *,
    user_id: int,
) -> list[FCMDevice]:

    stmt = (
        select(FCMDevice)
        .where(
            FCMDevice.user_id == user_id,
            FCMDevice.is_active.is_(True),
        )
        .order_by(
            FCMDevice.created_at.desc()
        )
    )

    return db.execute(stmt).scalars().all()


def deactivate_device(
    db: Session,
    *,
    user_id: int,
    device_id: int,
) -> bool:

    stmt = select(FCMDevice).where(
        FCMDevice.id == device_id,
        FCMDevice.user_id == user_id,
    )

    device = db.execute(stmt).scalar_one_or_none()

    if device is None:
        return False

    device.is_active = False

    db.commit()

    return True
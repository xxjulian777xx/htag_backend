import firebase_admin
from firebase_admin import credentials, messaging

from app.core.config import settings


def get_firebase_app():
    try:
        return firebase_admin.get_app()
    except ValueError:
        credential = credentials.Certificate(
            settings.fcm_credentials_path
        )

        return firebase_admin.initialize_app(
            credential
        )


def send_to_token(
    *,
    token: str,
    title: str,
    body: str,
    data: dict[str, str] | None = None,
) -> str:
    get_firebase_app()

    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        data=data or {},
        token=token,
    )

    return messaging.send(message)


def send_to_tokens(
    *,
    tokens: list[str],
    title: str,
    body: str,
    data: dict[str, str] | None = None,
) -> messaging.BatchResponse:

    get_firebase_app()

    if not tokens:
        raise ValueError(
            "La lista de tokens FCM no puede estar vacía"
        )

    message = messaging.MulticastMessage(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        data=data or {},
        tokens=tokens,
    )

    return messaging.send_each_for_multicast(message)
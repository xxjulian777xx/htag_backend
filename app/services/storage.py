from __future__ import annotations

import io
from functools import lru_cache

import boto3
from botocore.client import Config as BotoConfig
from botocore.exceptions import ClientError

from app.core.config import settings


@lru_cache
def get_storage_client():
    return boto3.client(
        "s3",
        endpoint_url=(
            f"http{'s' if settings.minio_secure else ''}://"
            f"{settings.minio_endpoint}"
        ),
        aws_access_key_id=settings.minio_root_user,
        aws_secret_access_key=settings.minio_root_password,
        region_name="us-east-1",
        config=BotoConfig(signature_version="s3v4"),
    )


def ensure_bucket() -> None:
    client = get_storage_client()

    try:
        client.head_bucket(Bucket=settings.minio_bucket)
        return
    except ClientError as exc:
        error_code = exc.response.get("Error", {}).get("Code")

        if error_code not in {"404", "NoSuchBucket", "NotFound"}:
            raise

    client.create_bucket(Bucket=settings.minio_bucket)


def upload_bytes(
    data: bytes,
    object_key: str,
    content_type: str,
) -> None:
    ensure_bucket()

    client = get_storage_client()

    client.upload_fileobj(
        io.BytesIO(data),
        settings.minio_bucket,
        object_key,
        ExtraArgs={
            "ContentType": content_type,
        },
    )


def delete_object(object_key: str) -> None:
    client = get_storage_client()

    client.delete_object(
        Bucket=settings.minio_bucket,
        Key=object_key,
    )


def object_exists(object_key: str) -> bool:
    client = get_storage_client()

    try:
        client.head_object(
            Bucket=settings.minio_bucket,
            Key=object_key,
        )
        return True
    except ClientError as exc:
        error_code = exc.response.get("Error", {}).get("Code")

        if error_code in {"404", "NoSuchKey", "NotFound"}:
            return False

        raise

    
def download_object(object_key: str) -> bytes:
    client = get_storage_client()

    response = client.get_object(
        Bucket=settings.minio_bucket,
        Key=object_key,
    )

    try:
        return response["Body"].read()
    finally:
        response["Body"].close()
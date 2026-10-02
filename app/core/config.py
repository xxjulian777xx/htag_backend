from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "RBAC Blog Informativo API"
    app_env: str = "development"
    app_debug: bool = True

    database_url: str

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"

    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    minio_endpoint: str
    minio_root_user: str
    minio_root_password: str
    minio_bucket: str = "media"
    minio_secure: bool = False

    fcm_credentials_path: str = "/app/firebase/firebase-service-account.json"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
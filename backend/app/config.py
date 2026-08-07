"""Centralized app settings, loaded from environment variables (.env in dev)."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # No accounts, no persistence -- this is a stateless prediction API, so
    # there's intentionally no database_url/jwt_secret here (see OpsDesk /
    # LinkPulse for repos where that's the point).
    cors_origins: list[str] = ["http://localhost:5173"]


@lru_cache
def get_settings() -> Settings:
    return Settings()

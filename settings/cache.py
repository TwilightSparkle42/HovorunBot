import os

from pydantic_settings import SettingsConfigDict

from .base import SettingsBase


class CacheSettings(SettingsBase):
    """
    Configure how the application connects to Valkey.

    Environment variables prefixed with ``CACHE_`` override the default host, port, and database index.
    """

    model_config = SettingsConfigDict(
        env_file=os.environ.get("CACHE_DOT_ENV", ".env"),
        env_prefix="CACHE_",
    )

    host: str = "localhost"
    port: int = 6379
    db: int = 0

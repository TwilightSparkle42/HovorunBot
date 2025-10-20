import os

from pydantic_settings import SettingsConfigDict

from .base import SettingsBase


class CacheSettings(SettingsBase):
    """
    Configuration for the Valkey cache connection.
    """

    model_config = SettingsConfigDict(
        env_file=os.environ.get("CACHE_DOT_ENV", ".env"),
        env_prefix="CACHE_",
    )

    host: str = "localhost"
    port: int = 6379
    db: int = 0

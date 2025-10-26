import os
from typing import Self

from injector import provider, singleton
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AdminSettings(BaseSettings):
    """
    Settings object for the admin panel interface.

    It is a mirror of the FastAdmin settings.
    """

    model_config = SettingsConfigDict(
        env_file=os.environ.get("ADMIN_DOT_ENV", ".env"),
        env_prefix="ADMIN_",
        extra="ignore",
    )
    secret_key: str | None = None
    base_url: str = "/"
    title: str = "Hovorun Admin"
    logo_url: str | None = None
    favicon_url: str | None = None
    templates_dir: str = "templates"
    debug: bool = False

    @classmethod
    @field_validator("secret_key")
    def validate_secret_key(cls, value: str | None) -> str:
        if value is None:
            raise ValueError("Secret key is not configured.")
        return value

    @classmethod
    @provider
    @singleton
    def build(cls) -> Self:
        return cls()

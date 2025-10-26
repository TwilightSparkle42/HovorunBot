import os
from typing import Self

from injector import provider, singleton

from .base import SettingsBase


class TelegramSettings(SettingsBase):
    class Config:
        env_file = os.environ.get("TELEGRAM_DOT_ENV", ".env")

    telegram_token: str | None = None
    telegram_bot_name: str | None = None

    @classmethod
    @provider
    @singleton
    def build(cls) -> Self:
        return cls()

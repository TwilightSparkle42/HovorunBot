import os

from .base import SettingsBase


class TelegramSettings(SettingsBase):
    class Config:
        env_file = os.environ.get("TELEGRAM_DOT_ENV", ".env")

    telegram_token: str | None = None

import os

from .base import SettingsBase


class GrokSettings(SettingsBase):
    class Config:
        env_file = os.environ.get("GROK_DOT_ENV", ".env")

    grok_api_key: str | None = None

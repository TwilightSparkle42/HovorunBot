import os

from .base import SettingsBase


class InfermaticSettings(SettingsBase):
    class Config:
        env_file = os.environ.get("INFERMATIC_DOT_ENV", ".env")

    infermatic_api_key: str | None = None

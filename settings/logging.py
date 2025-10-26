__all__ = ["LoggingSettings", "LogLevel"]

from typing import Literal, Self

from injector import provider, singleton

from settings.base import SettingsBase

LogLevel = Literal["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"]


class LoggingSettings(SettingsBase):
    """
    Runtime configuration for the standard logging subsystem.

    Fields intentionally mirror the subset of :mod:`logging` options we expose to the environment.
    """

    level: LogLevel = "INFO"
    format: str = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    datefmt: str = "%Y-%m-%dT%H:%M:%S%z"

    @classmethod
    @provider
    @singleton
    def build(cls) -> Self:
        return cls()

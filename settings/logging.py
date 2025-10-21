from __future__ import annotations

from typing import Literal

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


__all__ = ["LoggingSettings", "LogLevel"]

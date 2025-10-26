import logging
from logging.config import dictConfig
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from settings.logging import LoggingSettings

_configured = False


def configure_logging(settings: LoggingSettings) -> None:
    """
    Configure Python logging for the application.

    The configuration is idempotent to allow repeated initialisation in tests without
    mutating global logger state beyond the first invocation.
    """
    global _configured
    if _configured:
        return

    config = _build_config(settings)
    dictConfig(config)
    _configured = True


def _build_config(settings: LoggingSettings) -> dict[str, Any]:
    level_name = settings.level.upper()
    level = getattr(logging, level_name, logging.INFO)

    formatter_config = {
        "format": settings.format,
        "datefmt": settings.datefmt,
    }

    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": formatter_config,
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "standard",
                "level": level,
                "stream": "ext://sys.stdout",
            },
        },
        "root": {
            "level": level,
            "handlers": ["console"],
        },
    }

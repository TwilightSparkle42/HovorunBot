from threading import Lock

from injector import Injector

from ai_client.module import AiClientModule
from bot_runtime.module import BotRuntimeModule
from cache.module import CacheModule
from database.module import DatabaseModule
from errors import ConfigError
from logging_config.module import LoggingModule
from management.module import ManagementModule
from settings.module import SettingsModule

_injector: Injector | None = None
_injector_lock = Lock()


def setup_di() -> Injector:
    """
    Lazily construct and memoise the application's Injector instance.

    :returns: The configured :class:`injector.Injector` singleton.
    """
    module_classes = [
        SettingsModule,
        LoggingModule,
        AiClientModule,
        BotRuntimeModule,
        DatabaseModule,
        CacheModule,
        ManagementModule,
    ]

    global _injector
    with _injector_lock:
        _injector = _injector or Injector(modules=module_classes)
    if _injector is None:
        raise RuntimeError("Injector initialisation failed during setup.")
    return _injector


def get_injector() -> Injector:
    """
    Return the previously configured global Injector instance.

    :raises ConfigError: If the injector has not been initialised via :func:`setup_di`.
    :returns: The existing :class:`injector.Injector` instance.
    """
    if _injector is None:
        raise ConfigError("Injector is not initialised. Call setup_di() first.")
    return _injector

from threading import Lock

from injector import Injector

from ai_client.module import AiClientModule
from bot_runtime.module import BotRuntimeModule
from database.module import DatabaseModule
from errors import ConfigError
from settings.module import SettingsModule

_injector: Injector | None = None
_injector_lock = Lock()


def setup_di() -> Injector:
    """
    Lazily construct and memoise the application's Injector instance.

    Returns:
        Injector: The configured Injector singleton.
    """
    global _injector
    if _injector is None:
        with _injector_lock:
            if _injector is None:
                _injector = Injector(
                    modules=[
                        SettingsModule(),
                        AiClientModule(),
                        BotRuntimeModule(),
                        DatabaseModule(),
                    ]
                )
    return _injector


def get_injector() -> Injector:
    """
    Return the previously configured global Injector instance.

    Raises:
        ConfigError: If the injector was not initialised yet.
    """
    if _injector is None:
        raise ConfigError("Injector is not initialised. Call setup_di() first.")
    return _injector

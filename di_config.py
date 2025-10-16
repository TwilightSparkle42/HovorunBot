import injector

from settings.bot import TelegramSettings
from settings.infermatic import InfermaticSettings

_CONTAINER: injector.Injector | None = None


def setup_di() -> injector.Injector:
    global _CONTAINER
    if _CONTAINER is None:
        _CONTAINER = injector.Injector()
        _CONTAINER.binder.bind(TelegramSettings, to=TelegramSettings(), scope=injector.singleton)
        _CONTAINER.binder.bind(InfermaticSettings, to=InfermaticSettings(), scope=injector.singleton)
    return _CONTAINER


def get_injector() -> injector.Injector:
    """Return the global injector, initializing it if necessary."""
    global _CONTAINER
    if _CONTAINER is None:
        return setup_di()
    return _CONTAINER

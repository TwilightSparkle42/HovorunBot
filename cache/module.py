from injector import Binder, Module, singleton

from cache.telegram_update_storage import TelegramUpdateStorage
from cache.valkey import ValkeyCache


class CacheModule(Module):
    """
    Configure cache-related bindings for dependency injection.

    The module registers the Valkey cache client and Telegram update storage as singletons.
    """

    def configure(self, binder: Binder) -> None:
        binder.bind(ValkeyCache, to=ValkeyCache, scope=singleton)
        binder.bind(TelegramUpdateStorage, to=TelegramUpdateStorage, scope=singleton)

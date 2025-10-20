from injector import Binder, Module, singleton

from cache.telegram_update_storage import TelegramUpdateStorage
from cache.valkey import ValkeyCache


class CacheModule(Module):
    """Registers cache-related infrastructure with the injector."""

    def configure(self, binder: Binder) -> None:
        binder.bind(ValkeyCache, to=ValkeyCache, scope=singleton)
        binder.bind(TelegramUpdateStorage, to=TelegramUpdateStorage, scope=singleton)

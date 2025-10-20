from injector import Binder, Module, singleton

from settings.bot import TelegramSettings
from settings.cache import CacheSettings
from settings.database import DatabaseSettings
from settings.grok import GrokSettings
from settings.infermatic import InfermaticSettings


class SettingsModule(Module):
    def configure(self, binder: Binder) -> None:
        binder.bind(TelegramSettings, to=TelegramSettings(), scope=singleton)
        binder.bind(InfermaticSettings, to=InfermaticSettings(), scope=singleton)
        binder.bind(DatabaseSettings, to=DatabaseSettings(), scope=singleton)
        binder.bind(GrokSettings, to=GrokSettings(), scope=singleton)
        binder.bind(CacheSettings, to=CacheSettings(), scope=singleton)

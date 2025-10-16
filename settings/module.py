from injector import Module, Binder, singleton

from settings.bot import TelegramSettings
from settings.database import DatabaseSettings
from settings.infermatic import InfermaticSettings


class SettingsModule(Module):
    def configure(self, binder: Binder) -> None:
        binder.bind(TelegramSettings, to=TelegramSettings(), scope=singleton)
        binder.bind(InfermaticSettings, to=InfermaticSettings(), scope=singleton)
        binder.bind(DatabaseSettings, to=DatabaseSettings(), scope=singleton)

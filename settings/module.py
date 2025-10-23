from injector import Binder, Module, singleton

from settings.admin import AdminSettings
from settings.ai_client.grok_settings import GrokSettings
from settings.bot import TelegramSettings
from settings.cache import CacheSettings
from settings.database import DatabaseSettings


class SettingsModule(Module):
    def configure(self, binder: Binder) -> None:
        binder.bind(TelegramSettings, to=TelegramSettings(), scope=singleton)
        binder.bind(DatabaseSettings, to=DatabaseSettings(), scope=singleton)
        binder.bind(GrokSettings, to=GrokSettings(), scope=singleton)
        binder.bind(CacheSettings, to=CacheSettings(), scope=singleton)

        admin_panel = AdminSettings()
        admin_panel.patch_fastadmin()
        binder.bind(AdminSettings, to=admin_panel, scope=singleton)

from injector import Binder, Module, singleton

from bot_runtime import BotRuntime


class BotRuntimeModule(Module):
    """Provides bindings for bot runtime orchestration."""

    def configure(self, binder: Binder) -> None:
        binder.bind(BotRuntime, to=BotRuntime, scope=singleton)

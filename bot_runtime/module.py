from injector import Binder, Module, singleton

from bot_runtime import BotRuntime

from .message_handlers.ai_message import AiMessageHandler
from .message_handlers.base import HandlersRegistry
from .message_handlers.empty_chat_settings import EmptyChatSettingsHandler
from .message_handlers.empty_message import EmptyMessageHandler
from .message_handlers.not_allowed import NotAllowedHandler
from .message_handlers.test_message import TestMessageHandler


class BotRuntimeModule(Module):
    """Provides bindings for bot runtime orchestration."""

    def configure(self, binder: Binder) -> None:
        binder.bind(BotRuntime, to=BotRuntime, scope=singleton)

        handler_registry = HandlersRegistry()

        # TODO: replace with autodiscovery or other dynamic binding mechanism
        for handler in (
            EmptyChatSettingsHandler,
            EmptyMessageHandler,
            NotAllowedHandler,
            TestMessageHandler,
            AiMessageHandler,
        ):
            handler_registry.register(handler, binder.injector.create_object(handler))

        binder.bind(HandlersRegistry, to=handler_registry, scope=singleton)

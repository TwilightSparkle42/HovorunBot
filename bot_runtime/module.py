from injector import Binder, Module, singleton

from bot_runtime import BotRuntime

from .message_handlers.ai_message import AiMessageHandler
from .message_handlers.base import HandlersRegistry
from .message_handlers.empty_chat_settings import EmptyChatSettingsHandler
from .message_handlers.empty_message import EmptyMessageHandler
from .message_handlers.not_allowed import NotAllowedHandler
from .message_handlers.summarize_message import SummarizeMessageHandler
from .message_handlers.test_message import TestMessageHandler


class BotRuntimeModule(Module):
    """
    Configure dependency injection for bot runtime orchestration.

    The module wires the :class:`bot_runtime.BotRuntime` and registers all message handlers with the shared registry.
    """

    def configure(self, binder: Binder) -> None:
        binder.bind(BotRuntime, to=BotRuntime, scope=singleton)

        handler_registry = HandlersRegistry()

        # TODO: replace with autodiscovery or other dynamic binding mechanism
        # TODO: Move handler orchestration into a dedicated bootstrap that reads handler metadata once.
        #  Maintaining this tuple alongside DEPENDENCIES spreads ordering knowledge across files and is
        #  the current pain point when experimenting with new handlers or restructuring the hierarchy.
        for handler in (
            EmptyChatSettingsHandler,
            EmptyMessageHandler,
            NotAllowedHandler,
            SummarizeMessageHandler,
            TestMessageHandler,
            AiMessageHandler,
        ):
            handler_registry.register(handler, binder.injector.create_object(handler))

        binder.bind(HandlersRegistry, to=handler_registry, scope=singleton)

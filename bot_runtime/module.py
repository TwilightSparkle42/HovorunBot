from injector import Binder, Module, singleton
from telegram.ext import CommandHandler, MessageHandler, filters

from .message_handlers import discover_handler_types
from .message_handlers.base import HandlersRegistry
from .message_pipeline import MessageHandlerPipeline
from .runtime import BotRuntime
from .telegram_handlers import TelegramHandlerRegistration, TelegramHandlersSet


class BotRuntimeModule(Module):
    """
    Configure dependency injection for bot runtime orchestration.

    The module wires the :class:`bot_runtime.BotRuntime` and registers all message handlers with the shared registry.
    """

    def configure(self, binder: Binder) -> None:
        binder.bind(BotRuntime, to=BotRuntime, scope=singleton)

        handler_registry = HandlersRegistry()
        injector = binder.injector
        if injector is None:
            raise RuntimeError("Injector is not initialised while configuring BotRuntimeModule.")

        for handler_type in discover_handler_types():
            handler_registry.register(handler_type, injector.create_object(handler_type))

        binder.bind(HandlersRegistry, to=handler_registry, scope=singleton)
        binder.bind(MessageHandlerPipeline, to=MessageHandlerPipeline(handler_registry), scope=singleton)

        telegram_handlers = TelegramHandlersSet(
            registrations=[
                TelegramHandlerRegistration(lambda runtime: CommandHandler("start", runtime.start_command)),
                TelegramHandlerRegistration(
                    lambda runtime: MessageHandler(filters.TEXT & ~filters.COMMAND, runtime.handle_message)
                ),
            ]
        )
        binder.bind(TelegramHandlersSet, to=telegram_handlers, scope=singleton)

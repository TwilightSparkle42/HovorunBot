__all__ = ["TelegramHandlerRegistration", "TelegramHandlersSet"]

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, Sequence

from telegram.ext import Application
from telegram.ext import BaseHandler as TelegramBaseHandler

if TYPE_CHECKING:
    from bot_runtime.runtime import BotRuntime

HandlerFactory = Callable[["BotRuntime"], TelegramBaseHandler[Any, Any, Any]]


@dataclass(frozen=True)
class TelegramHandlerRegistration:
    """
    Describe how to construct and register a Telegram handler.

    :param factory: Callable that receives the current :class:`BotRuntime` instance and returns a handler.
    :param group: Optional dispatcher group used when registering the handler.
    """

    factory: HandlerFactory
    group: int | None = None

    def build(self, runtime: "BotRuntime") -> TelegramBaseHandler[Any, Any, Any]:
        handler = self.factory(runtime)
        if handler is None:
            raise ValueError("Telegram handler factory returned None.")
        return handler


class TelegramHandlersSet:
    """
    Container that encapsulates Telegram handler registrations for the runtime.
    """

    def __init__(self, registrations: Sequence[TelegramHandlerRegistration]) -> None:
        self._registrations = list(registrations)

    def register_all(self, application: Application[Any, Any, Any, Any, Any, Any], runtime: "BotRuntime") -> None:
        """
        Register all configured handlers against the provided application instance.

        :param application: Telegram application to extend.
        :param runtime: Bot runtime providing callbacks for the handlers.
        """
        for registration in self._registrations:
            handler = registration.build(runtime)
            if registration.group is None:
                application.add_handler(handler)
            else:
                application.add_handler(handler, registration.group)

    def registrations(self) -> list[TelegramHandlerRegistration]:
        """
        Return a copy of the handler registrations.

        :returns: List of handler registrations.
        """
        return list(self._registrations)

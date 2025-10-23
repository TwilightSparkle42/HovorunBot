from functools import cached_property

from telegram import Update

from bot_runtime.message_handlers.base import BaseHandler, HandlersRegistry
from bot_types import Context
from database.models import ChatConfiguration
from logging_config.common import WithLogger
from utils.dependable import sort_topologically

__all__ = ["MessageHandlerPipeline"]


class MessageHandlerPipeline(WithLogger):
    """
    Execute message handlers according to their declared dependencies.

    The pipeline resolves a deterministic order once, then evaluates each handler's eligibility via
    :meth:`BaseHandler.can_handle`. When a handler processes the update, the pipeline stops unless the handler opts
    in to continuation by setting :attr:`BaseHandler.continue_after_handle`.
    """

    def __init__(self, registry: HandlersRegistry) -> None:
        self._registry = registry

    @cached_property
    def ordered_handlers(self) -> tuple[BaseHandler, ...]:
        return tuple(self._build_ordered_handlers())

    async def dispatch(
        self, update: Update, context: Context, chat_settings: ChatConfiguration | None, *, chat_id: int | None
    ) -> bool:
        """
        Run the pipeline for the given update.

        :param update: Telegram update to process.
        :param context: Bot execution context.
        :param chat_settings: Persisted chat configuration, if available.
        :param chat_id: Resolved chat identifier used for logging.
        :returns: ``True`` when at least one handler accepted the update.
        """
        handled = False
        for handler in self.ordered_handlers:
            name = handler.__class__.__name__
            if not handler.can_handle(update, context, chat_settings):
                self._logger.debug(
                    "Handler %s skipped update %s for chat %s",
                    name,
                    update.update_id,
                    chat_id,
                )
                continue

            self._logger.info(
                "Dispatching handler %s for update %s (chat=%s)",
                name,
                update.update_id,
                chat_id,
            )
            await handler.handle(update, context, chat_settings)
            handled = True
            if not handler.continue_after_handle:
                break

        return handled

    def _build_ordered_handlers(self) -> list[BaseHandler]:
        handler_types = sort_topologically(self._registry.keys())
        return [self._registry.get(handler_type) for handler_type in handler_types]

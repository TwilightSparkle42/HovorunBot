from injector import Inject
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from bot_runtime.message_handlers.base import BaseHandler, HandlersRegistry
from bot_types import Context
from cache.telegram_update_storage import TelegramUpdateStorage
from database.chat_access_repository import ChatAccessRepository
from database.models import ChatAccess
from errors import ConfigError
from logging_config.common import WithLogger
from settings.bot import TelegramSettings
from utils.dependable import sort_topologically


class BotRuntime(WithLogger):
    def __init__(
        self,
        telegram_settings: Inject[TelegramSettings],
        handlers: Inject[HandlersRegistry],
        chat_access_repository: Inject[ChatAccessRepository],
        update_storage: Inject[TelegramUpdateStorage],
    ) -> None:
        self._settings = telegram_settings
        if self._settings.telegram_token is None:
            raise ConfigError("Telegram token is not provided, bot cannot be started.")
        self._application = Application.builder().token(self._settings.telegram_token).build()
        self._handlers = handlers
        self._chat_access_repository = chat_access_repository
        self._update_storage = update_storage
        self.add_handlers()

    def add_handlers(self) -> None:
        # Register command handlers
        # TODO: Generalize handler registration by injecting a configurable list of command/message handlers
        #  instead of hardcoding them here.
        self._application.add_handler(CommandHandler("start", self.start_command))

        # Register message handlers (filters for text messages not starting with '/')
        self._application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

    def run(self) -> None:
        poll_interval = 3
        self._logger.info("Starting Telegram polling (interval=%s seconds)", poll_interval)
        self._application.run_polling(poll_interval=poll_interval)

    # Command handler for /start
    async def start_command(self, update: Update, _: Context):
        await self._update_storage.store(update)
        if update.message is None:
            return
        record = await self._ensure_chat_access(update)
        if record is None:
            return
        if not record.allowed:
            await self._notify_not_allowed(update)
            return
        await update.message.reply_text("Hello! I am your bot. How can I help you?")

    # Message handler for plain text messages
    async def handle_message(self, update: Update, context: Context):
        await self._update_storage.store(update)
        chat_settings = await self._ensure_chat_access(update)
        chat_id = update.effective_chat.id if update.effective_chat else None
        self._logger.info("Processing inbound update %s for chat %s", update.update_id, chat_id)
        handler_types: list[type[BaseHandler]] = sort_topologically(self._handlers.keys())
        # TODO: Replace this manual loop with a pipeline/strategy executor that can compose multiple handlers.
        #  Right now we return after the first hit, which makes orchestration brittle, duplicates dependency logic,
        #  and prevents cross-cutting concerns (e.g. auditing, analytics) from running alongside the main responder.
        for handler_cls in handler_types:
            handler = self._handlers.get(handler_cls)
            if not handler.can_handle(update, context, chat_settings):
                self._logger.debug(
                    "Handler %s cannot handle update %s",
                    handler.__class__.__name__,
                    update.update_id,
                )
                continue
            self._logger.info(
                "Dispatching handler %s for update %s",
                handler.__class__.__name__,
                update.update_id,
            )
            await handler.handle(update, context, chat_settings)
            return

        self._logger.info("No handler accepted update %s", update.update_id)

    async def _ensure_chat_access(self, update: Update) -> ChatAccess | None:
        chat = update.effective_chat
        if chat is None:
            return None
        return await self._chat_access_repository.ensure_exists(str(chat.id))

    async def _notify_not_allowed(self, update: Update):
        if not update.message:
            return

        chat_id = update.effective_chat.id if update.effective_chat else None
        self._logger.info("Access denied for chat %s", chat_id)
        await update.message.reply_text("Access pending approval. Please contact the administrator.")


__all__ = ["BotRuntime"]

import logging

from injector import Inject
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from bot_runtime.message_handlers.base import HandlersRegistry
from bot_types import Context
from cache.telegram_update_storage import TelegramUpdateStorage
from database.chat_access_repository import ChatAccessRepository
from database.models import ChatAccess
from errors import ConfigError
from settings.bot import TelegramSettings
from utils.dependable import sort_topologically


class BotRuntime:
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
        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.INFO)

    def add_handlers(self) -> None:
        # Register command handlers
        # TODO: Generalize handler registration by injecting a configurable list of command/message handlers
        #  instead of hardcoding them here.
        self._application.add_handler(CommandHandler("start", self.start_command))

        # Register message handlers (filters for text messages not starting with '/')
        self._application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

    def run(self) -> None:
        self._logger.info("Starting bot with polling interval of 3 seconds...")
        print("Starting bot with polling interval of 3 seconds...")
        self._application.run_polling(poll_interval=3)

    # Command handler for /start
    async def start_command(self, update: Update, _: Context):
        await self._update_storage.store(update)
        if update.message is None:
            return
        record = self._ensure_chat_access(update)
        if record is None:
            return
        if not record.allowed:
            await self._notify_not_allowed(update)
            return
        await update.message.reply_text("Hello! I am your bot. How can I help you?")

    # Message handler for plain text messages
    async def handle_message(self, update: Update, context: Context):
        await self._update_storage.store(update)
        chat_settings = self._ensure_chat_access(update)
        for handler_cls in sort_topologically(self._handlers.keys()):
            handler = self._handlers.get(handler_cls)
            if not handler.can_handle(update, context, chat_settings):
                print(f"Handler {handler.__class__.__name__} does not handle the message.")
                continue
            print(f"Handling message with handler: {handler.__class__.__name__}")
            await handler.handle(update, context, chat_settings)
            return

    def _ensure_chat_access(self, update: Update) -> ChatAccess | None:
        chat = update.effective_chat
        if chat is None:
            return None
        return self._chat_access_repository.ensure_exists(str(chat.id))

    async def _notify_not_allowed(self, update: Update):
        if not update.message:
            return

        await update.message.reply_text("Access pending approval. Please contact the administrator.")


__all__ = ["BotRuntime"]

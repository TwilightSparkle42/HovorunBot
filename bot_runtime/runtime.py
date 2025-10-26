__all__ = ["BotRuntime"]

from injector import Inject
from telegram import Update
from telegram.ext import Application

from bot_runtime.message_pipeline import MessageHandlerPipeline
from bot_runtime.telegram_handlers import TelegramHandlersSet
from bot_types import Context
from cache.telegram_update_storage import TelegramUpdateStorage
from database.models import ChatConfiguration
from errors import ConfigError
from logging_config.common import WithLogger
from services.chat_service import ChatService
from settings.bot import TelegramSettings


class BotRuntime(WithLogger):
    def __init__(
        self,
        telegram_settings: Inject[TelegramSettings],
        telegram_handlers: Inject[TelegramHandlersSet],
        message_pipeline: Inject[MessageHandlerPipeline],
        update_storage: Inject[TelegramUpdateStorage],
        chat_service: Inject[ChatService],
    ) -> None:
        self._settings = telegram_settings
        if self._settings.telegram_token is None:
            raise ConfigError("Telegram token is not provided, bot cannot be started.")
        self._application = Application.builder().token(self._settings.telegram_token).build()
        self._telegram_handlers = telegram_handlers
        self._message_pipeline = message_pipeline
        self._update_storage = update_storage
        self._chat_service = chat_service
        self.add_handlers()

    def add_handlers(self) -> None:
        self._telegram_handlers.register_all(self._application, self)

    def run(self) -> None:
        poll_interval = 3
        self._logger.info("Starting Telegram polling (interval=%s seconds)", poll_interval)
        self._application.run_polling(poll_interval=poll_interval)

    async def start_command(self, update: Update, _: Context) -> None:
        await self._update_storage.store(update)
        if update.message is None:
            return
        record = await self._ensure_chat_configuration(update)
        if record is None:
            return
        if not record.allowed:
            await self._notify_not_allowed(update)
            return
        await update.message.reply_text("Hello! I am your bot. How can I help you?")

    async def handle_message(self, update: Update, context: Context) -> None:
        await self._update_storage.store(update)
        chat_settings = await self._ensure_chat_configuration(update)
        chat_id = update.effective_chat.id if update.effective_chat else None
        self._logger.info("Processing inbound update %s for chat %s", update.update_id, chat_id)
        handled = await self._message_pipeline.dispatch(
            update,
            context,
            chat_settings,
            chat_id=chat_id,
        )
        if not handled:
            self._logger.info("No handler accepted update %s for chat %s", update.update_id, chat_id)

    async def _ensure_chat_configuration(self, update: Update) -> ChatConfiguration | None:
        chat = update.effective_chat
        if chat is None:
            return None
        return await self._chat_service.ensure_exists(
            str(chat.id),
            title=chat.title,
            chat_type=chat.type,
        )

    async def _notify_not_allowed(self, update: Update) -> None:
        if not update.message:
            return

        chat_id = update.effective_chat.id if update.effective_chat else None
        self._logger.info("Access denied for chat %s", chat_id)
        await update.message.reply_text("Access pending approval. Please contact the administrator.")

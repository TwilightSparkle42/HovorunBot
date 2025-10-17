import logging
from functools import partial
from typing import Sequence

from injector import Inject
from telegram import Bot, Update, User
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from ai_client.base import AiClientRegistry, BaseAiClient
from bot_types import Context
from database.chat_access_repository import ChatAccessRepository
from database.models import ChatAccess
from errors import ConfigError
from settings.bot import TelegramSettings


class BotRuntime:
    def __init__(
        self,
        telegram_settings: Inject[TelegramSettings],
        ai_registry: Inject[AiClientRegistry],
        chat_access_repository: Inject[ChatAccessRepository],
    ) -> None:
        self._settings = telegram_settings
        if self._settings.telegram_token is None:
            raise ConfigError("Telegram token is not provided, bot cannot be started.")
        self._application = Application.builder().token(self._settings.telegram_token).build()
        self._ai_registry = ai_registry
        self._chat_access_repository = chat_access_repository
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
        record = self._ensure_chat_access(update)
        if record is None:
            return
        if update.message is None or update.message.text is None:
            return
        user_message = update.message.text.lower()
        if user_message.startswith("#test"):
            await update.message.reply_text(f"Hi there! You said: {user_message}")
            return
        if not record.allowed:
            await self._notify_not_allowed(update)
            return
        # TODO: Replace hard-coded pattern matching with a pluggable responder pipeline so new triggers can be added
        # without modifying this method.
        message_chain: Sequence[tuple[str, str]] | None = None
        match user_message:
            case user_message if "hey bro" in user_message:
                message_chain = await self._collect_reply_chain(update, context.bot)
            case _ if (
                update.message.reply_to_message
                and self._is_same_user(update.message.reply_to_message.from_user, context.bot)  # type: ignore[union-attr]
            ):
                message_chain = await self._collect_reply_chain(update, context.bot)
        if message_chain is None:
            return

        ai_client = self._resolve_ai_client(record)
        await self._ask_ai(update, message_chain, ai_client)

    def _is_same_user(self, user1: User | Bot, user2: User | Bot) -> bool:
        return user1.id == user2.id

    async def _collect_reply_chain(self, update: Update, app: Bot) -> Sequence[tuple[str, str]]:
        result = []
        is_bot_message = partial(self._is_same_user, app)
        if is_bot_message(update.message.from_user):
            result.append(("assistant", update.message.text))
        else:
            result.append((update.message.from_user.name, update.message.text))
        current_message = update.message
        while current_message.reply_to_message:
            if is_bot_message(current_message.reply_to_message.from_user):
                result.append(("assistant", current_message.reply_to_message.text))
            else:
                result.append((current_message.reply_to_message.from_user.name, current_message.reply_to_message.text))
            current_message = current_message.reply_to_message
        return result

    async def _ask_ai(
        self,
        update: Update,
        message: Sequence[tuple[str, str]],
        ai_client: BaseAiClient,
    ) -> None:
        answer = await ai_client.answer(message)
        await update.message.reply_text(answer)  # type: ignore[union-attr]

    def _resolve_ai_client(self, record: ChatAccess) -> BaseAiClient:
        provider = record.provider or ChatAccess.DEFAULT_PROVIDER
        if not self._ai_registry.contains(provider):
            raise ConfigError(f"AI provider '{provider}' is not registered.")
        return self._ai_registry.get(provider)

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

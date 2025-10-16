import logging

from injector import Inject
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from ai_client import InfermaticAiClient
from bot_types import Context
from errors import ConfigError
from settings.bot import TelegramSettings


class BotRuntime:
    def __init__(self, telegram_settings: Inject[TelegramSettings], ai_client: Inject[InfermaticAiClient]) -> None:
        self._settings = telegram_settings
        if self._settings.telegram_token is None:
            raise ConfigError("Telegram token is not provided, bot cannot be started.")
        self._application = Application.builder().token(self._settings.telegram_token).build()
        self._ai_client = ai_client
        self.add_handlers()
        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.INFO)

    def add_handlers(self) -> None:
        # Register command handlers
        self._application.add_handler(CommandHandler("start", self.start_command))
        self._application.add_handler(CommandHandler("known_models", self.known_models_command))

        # Register message handlers (filters for text messages not starting with '/')
        self._application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

    def run(self) -> None:
        self._logger.info("Starting bot with polling interval of 3 seconds...")
        print("Starting bot with polling interval of 3 seconds...")
        self._application.run_polling(poll_interval=3)

    # Command handler for /start
    async def start_command(self, update: Update, _: Context):
        await update.message.reply_text("Hello! I am your bot. How can I help you?")

    async def known_models_command(self, update: Update, _: Context):
        await update.message.reply_text(str(await self._ai_client.get_known_models()))

    # Message handler for plain text messages
    async def handle_message(self, update: Update, context: Context):
        user_message = update.message.text.lower()
        match user_message:
            case user_message if "hey bro" in user_message:
                await self._ask_ai(update, user_message)
            case _ if (
                update.message.reply_to_message and update.message.reply_to_message.from_user.id == context.bot.id
            ):
                await self._ask_ai(update, user_message)
            case user_message if user_message.startswith("#test"):
                await update.message.reply_text(f"Hi there! You said: {user_message}")

    async def _ask_ai(self, update: Update, message: str) -> None:
        answer = await self._ai_client.answer(message)
        await update.message.reply_text(answer)

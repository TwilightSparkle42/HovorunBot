from typing import cast

from telegram import Message, Update

from bot_types import Context
from database.models import ChatConfiguration

from .base import BaseHandler
from .not_allowed import NotAllowedHandler


class TestMessageHandler(BaseHandler):
    DEPENDENCIES = (NotAllowedHandler,)

    def can_handle(self, update: Update, context: Context, chat_settings: ChatConfiguration | None) -> bool:
        del context
        if chat_settings is None or chat_settings.allowed is not True:
            return False
        message = update.message
        if message is None or message.text is None:
            return False
        return message.text.startswith("#test")

    async def handle(self, update: Update, context: Context, chat_settings: ChatConfiguration | None) -> None:
        del context, chat_settings
        message = cast(Message, update.message)
        if message.text is None:
            await message.reply_text("Hi there! I could not read your message.")
            return
        await message.reply_text(f"Hi there! You said: {message.text}")

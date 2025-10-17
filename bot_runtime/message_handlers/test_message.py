from typing import cast

from telegram import Message, Update

from bot_types import Context
from database.models import ChatAccess

from .base import BaseHandler
from .not_allowed import NotAllowedHandler


class TestMessageHandler(BaseHandler):
    DEPENDENCIES = (NotAllowedHandler,)

    def can_handle(self, update: Update, context: Context, chat_settings: ChatAccess | None) -> bool:
        if chat_settings is None or chat_settings.allowed is not True:
            return False
        message = cast(Message, update.message)
        return message.text.startswith("#test")

    async def handle(self, update: Update, context: Context, chat_settings: ChatAccess | None) -> None:
        message = cast(Message, update.message)
        await message.reply_text(f"Hi there! You said: {message.text}")

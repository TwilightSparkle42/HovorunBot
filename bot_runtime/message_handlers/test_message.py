from typing import cast

from telegram import Message, Update

from bot_types import Context
from database.models import ChatAccess

from .base import BaseHandler


class TestMessageHandler(BaseHandler):
    def can_handle(self, update: Update, context: Context, chat_settings: ChatAccess | None) -> bool:
        if chat_settings is None or chat_settings.allowed is not True:
            return False
        message = cast(Message, update.message)
        text = message.text or ""
        return text.startswith("#test")

    async def handle(self, update: Update, context: Context, chat_settings: ChatAccess | None) -> bool:
        message = cast(Message, update.message)
        await message.reply_text(f"Hi there! You said: {message.text}")
        return True

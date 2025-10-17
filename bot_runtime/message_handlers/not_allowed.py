from typing import cast

from telegram import Message, Update

from bot_types import Context
from database.models import ChatAccess

from .base import BaseHandler


class NotAllowedHandler(BaseHandler):
    def can_handle(self, update: Update, context: Context, chat_settings: ChatAccess | None) -> bool:
        return chat_settings is not None and chat_settings.allowed is False

    async def handle(self, update: Update, context: Context, chat_settings: ChatAccess | None) -> bool:
        message = cast(Message, update.message)
        await message.reply_text("Access pending approval. Please contact the administrator.")
        return True

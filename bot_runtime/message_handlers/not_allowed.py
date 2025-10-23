from typing import cast

from telegram import Message, Update

from bot_types import Context
from database.models import ChatConfiguration

from .base import BaseHandler
from .empty_chat_settings import EmptyChatSettingsHandler


class NotAllowedHandler(BaseHandler):
    DEPENDENCIES = (EmptyChatSettingsHandler,)

    def can_handle(self, update: Update, context: Context, chat_settings: ChatConfiguration | None) -> bool:
        del update, context
        return chat_settings is not None and chat_settings.allowed is False

    async def handle(self, update: Update, context: Context, chat_settings: ChatConfiguration | None) -> None:
        del context, chat_settings
        message = cast(Message, update.message)
        await message.reply_text("Access pending approval. Please contact the administrator.")

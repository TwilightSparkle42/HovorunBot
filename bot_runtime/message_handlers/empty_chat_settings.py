from telegram import Update

from bot_types import Context
from database.models import ChatConfiguration

from .base import BaseHandler


class EmptyChatSettingsHandler(BaseHandler):
    def can_handle(self, update: Update, context: Context, chat_settings: ChatConfiguration | None) -> bool:
        del update, context
        return chat_settings is None

    async def handle(self, update: Update, context: Context, chat_settings: ChatConfiguration | None) -> None:
        del update, context, chat_settings

from telegram import Update

from bot_types import Context
from database.models import ChatAccess

from .base import BaseHandler


class EmptyChatSettingsHandler(BaseHandler):
    def can_handle(self, update: Update, context: Context, chat_settings: ChatAccess | None) -> bool:
        return chat_settings is None

    async def handle(self, update: Update, context: Context, chat_settings: ChatAccess | None) -> None:
        return None

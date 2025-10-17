from telegram import Update

from bot_types import Context
from database.models import ChatAccess

from .base import BaseHandler


class EmptyMessageHandler(BaseHandler):
    def can_handle(self, update: Update, context: Context, chat_settings: ChatAccess | None) -> bool:
        if update.message is None:
            return True
        if update.message.text is None:
            return True
        return False

    async def handle(self, update: Update, context: Context, chat_settings: ChatAccess | None) -> None:
        return None

from telegram import Update

from bot_types import Context
from database.models import ChatAccess

from .base import BaseHandler
from .not_allowed import NotAllowedHandler


class EmptyMessageHandler(BaseHandler):
    DEPENDENCIES = (NotAllowedHandler,)

    def can_handle(self, update: Update, context: Context, chat_settings: ChatAccess | None) -> bool:
        return update.message is None or update.message.text is None

    async def handle(self, update: Update, context: Context, chat_settings: ChatAccess | None) -> None:
        return None

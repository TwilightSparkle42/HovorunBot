from telegram import Update

from bot_types import Context
from database.models import ChatConfiguration

from .base import BaseHandler
from .not_allowed import NotAllowedHandler


class EmptyMessageHandler(BaseHandler):
    DEPENDENCIES = (NotAllowedHandler,)

    def can_handle(self, update: Update, context: Context, chat_settings: ChatConfiguration | None) -> bool:
        del context, chat_settings
        return update.message is None or update.message.text is None

    async def handle(self, update: Update, context: Context, chat_settings: ChatConfiguration | None) -> None:
        del update, context, chat_settings

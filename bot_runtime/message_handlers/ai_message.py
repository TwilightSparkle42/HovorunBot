from typing import Sequence, cast

from injector import Inject
from telegram import Bot, Message, Update

from ai_client.base import AiClientRegistry
from bot_types import Context
from database.models import ChatAccess
from settings.bot import TelegramSettings

from .base import BaseHandler
from .helpers import build_message_chain, is_same_user, reply_chain_to_records, resolve_ai_client
from .summarize_message import SummarizeMessageHandler


class AiMessageHandler(BaseHandler):
    DEPENDENCIES = (SummarizeMessageHandler,)

    def __init__(self, ai_registry: Inject[AiClientRegistry], bot_settings: Inject[TelegramSettings]) -> None:
        self._ai_registry = ai_registry
        self._bot_settings = bot_settings

    def can_handle(self, update: Update, context: Context, chat_settings: ChatAccess | None) -> bool:
        message = update.message
        if message is None or message.text is None:
            return False
        bot_name = self._bot_settings.telegram_bot_name
        if bot_name and bot_name in message.text:
            return True
        reply_to = message.reply_to_message
        return bool(reply_to and reply_to.from_user and is_same_user(reply_to.from_user, context.bot))

    async def handle(self, update: Update, context: Context, chat_settings: ChatAccess | None) -> None:
        assert chat_settings is not None, "Chat access record is required."
        message = cast(Message, update.message)
        # TODO: Inject per-chat persona/model settings (system prompts, temperature overrides, etc.).
        #  We only respect `ChatAccess.provider`, so all other behavioural tweaks are currently hard-coded.
        message_chain = await self._collect_reply_chain(message, context.bot)
        ai_client = resolve_ai_client(self._ai_registry, chat_settings)
        answer = await ai_client.answer(message_chain)
        await message.reply_text(answer)

    async def _collect_reply_chain(self, message: Message, bot: Bot) -> Sequence[tuple[str, str]]:
        records = reply_chain_to_records(message)
        # TODO: Allow chat-configured system prefixes so responses can be tailored per conversation.
        return build_message_chain(records, bot)

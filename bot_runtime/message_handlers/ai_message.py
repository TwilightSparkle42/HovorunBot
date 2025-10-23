from typing import Sequence, cast

from injector import Inject
from telegram import Bot, Message, Update

from ai_client.base import AiClientRegistry, AiMessage
from bot_types import Context
from database.models import ChatConfiguration
from logging_config.common import WithLogger
from settings.bot import TelegramSettings
from utils.message_chain import build_message_chain, is_same_user, reply_chain_to_records, resolve_ai_client

from .base import BaseHandler
from .summarize_message import SummarizeMessageHandler


class AiMessageHandler(WithLogger, BaseHandler):
    DEPENDENCIES = (SummarizeMessageHandler,)

    def __init__(self, ai_registry: Inject[AiClientRegistry], bot_settings: Inject[TelegramSettings]) -> None:
        self._ai_registry = ai_registry
        self._bot_settings = bot_settings

    def can_handle(self, update: Update, context: Context, chat_settings: ChatConfiguration | None) -> bool:
        if chat_settings is None or chat_settings.allowed is not True:
            return False
        message = update.message
        if message is None or message.text is None:
            return False
        bot_name = self._bot_settings.telegram_bot_name
        if bot_name and bot_name in message.text:
            return True
        reply_to = message.reply_to_message
        return bool(reply_to and reply_to.from_user and is_same_user(reply_to.from_user, context.bot))

    async def handle(self, update: Update, context: Context, chat_settings: ChatConfiguration | None) -> None:
        if chat_settings is None:
            self._logger.warning("Chat settings missing while handling AI message; skipping response.")
            return
        message = cast(Message, update.message)
        # TODO: Inject per-chat persona/model settings (system prompts, temperature overrides, etc.).
        #  We currently respect only `ChatConfiguration.model_configuration`, so other tweaks remain hard-coded.
        message_chain = await self._collect_reply_chain(message, context.bot)
        ai_client = resolve_ai_client(self._ai_registry, chat_settings)
        chat_ref = chat_settings.chat.telegram_chat_id if chat_settings.chat else "unknown"

        self._logger.info(
            "Prepared message chain with %s entries for chat %s",
            len(message_chain),
            chat_ref,
        )
        self._logger.info(
            "Requesting AI response from %s for chat %s (message_id=%s)",
            ai_client.get_name(),
            chat_ref,
            message.message_id,
        )
        model_configuration = chat_settings.model_configuration
        answer = await ai_client.answer(message_chain, model_configuration)
        self._logger.info(
            "Received AI response from %s for chat %s (message_id=%s)",
            ai_client.get_name(),
            chat_ref,
            message.message_id,
        )
        await message.reply_text(answer)

    async def _collect_reply_chain(self, message: Message, bot: Bot) -> Sequence[AiMessage]:
        records = reply_chain_to_records(message)
        # TODO: Allow chat-configured system prefixes so responses can be tailored per conversation.
        return build_message_chain(records, bot)

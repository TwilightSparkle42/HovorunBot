import re
from typing import Final, Sequence, cast

from injector import Inject
from telegram import Bot, Message, Update

from ai_client.base import AiClientRegistry
from bot_types import Context
from cache.telegram_update_storage import TelegramUpdateRecord, TelegramUpdateStorage
from database.models import ChatAccess
from logging_config.common import WithLogger

from .base import BaseHandler
from .helpers import build_message_chain, resolve_ai_client
from .not_allowed import NotAllowedHandler


class SummarizeMessageHandler(WithLogger, BaseHandler):
    """
    Handle summarisation commands by aggregating chat history from Valkey.

    Recent messages are compiled into an AI-ready prompt and sent to the configured provider to generate a concise
    recap.
    """

    DEPENDENCIES = (NotAllowedHandler,)
    _SUMMARY_KEYWORDS: tuple[str, ...] = (
        "#summarize",
        "#підсумуй",
    )
    _COMMAND_PATTERN: Final[re.Pattern[str]] = re.compile(rf"^({'|'.join(_SUMMARY_KEYWORDS)})\s*(\d+)", re.IGNORECASE)
    _MAX_MESSAGES: Final[int] = 200

    def __init__(
        self,
        ai_registry: Inject[AiClientRegistry],
        update_storage: Inject[TelegramUpdateStorage],
    ) -> None:
        self._ai_registry = ai_registry
        self._update_storage = update_storage

    def can_handle(self, update: Update, context: Context, chat_settings: ChatAccess | None) -> bool:
        message = update.message
        if message is None or message.text is None:
            return False
        if not message.text.startswith(self._SUMMARY_KEYWORDS):
            return False
        return self._COMMAND_PATTERN.match(message.text) is not None

    async def handle(self, update: Update, context: Context, chat_settings: ChatAccess | None) -> None:
        message = update.message
        if message is None or message.text is None:
            return None
        telegram_message = cast(Message, message)

        match = self._COMMAND_PATTERN.match(message.text)
        if match is None:
            await telegram_message.reply_text("Invalid summarize command format.")
            return None
        limit = int(match.group(2))
        if limit <= 0:
            await telegram_message.reply_text("Invalid limit. You must specify a positive number.")
            return None

        if limit > self._MAX_MESSAGES:
            limit = self._MAX_MESSAGES
            await telegram_message.reply_text(
                f"Limit is greater than the maximum allowed ({self._MAX_MESSAGES}). Using {limit}."
            )

        assert chat_settings is not None, "Chat access record is required."
        history = await self._retrieve_history(chat_id=int(chat_settings.chat_id), limit=limit)
        self._logger.info(
            "Retrieved %s cached messages for chat %s (limit=%s)",
            len(history),
            chat_settings.chat_id,
            limit,
        )
        message_chain = await self._collect_reply_chain(history, context.bot)
        ai_client = resolve_ai_client(self._ai_registry, chat_settings)
        self._logger.info(
            "Requesting summary from %s for chat %s (limit=%s)",
            ai_client.get_name(),
            chat_settings.chat_id,
            limit,
        )
        response = await ai_client.answer(message_chain)
        self._logger.info(
            "Received summary response from %s for chat %s",
            ai_client.get_name(),
            chat_settings.chat_id,
        )
        await telegram_message.reply_text(response)
        return None

    async def _collect_reply_chain(
        self, messages: Sequence[TelegramUpdateRecord], bot: Bot
    ) -> Sequence[tuple[str, str]]:
        prefix = [
            (
                "system",
                "You are a helpful friend to assist. You need to go through the messages of the conversation "
                "and summarize in general what has been discussed. Do not make up your own ideas. Be concise. "
                "Do not include any personal opinion until you directly asked.",
            )
        ]
        # TODO: Pull the summary/system prompt from chat-level configuration instead of hard-coding English text.
        #  Different groups will want localized or domain-specific summaries.
        return build_message_chain(messages, bot, prefix=prefix)

    async def _retrieve_history(self, chat_id: int, limit: int) -> list[TelegramUpdateRecord]:
        return await self._update_storage.get_last_messages(chat_id=chat_id, limit=limit)

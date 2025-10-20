import logging
import re
from functools import partial
from typing import Final, Sequence, cast

from injector import Inject
from telegram import Bot, Message, Update, User

from ai_client.base import AiClientRegistry, BaseAiClient
from bot_types import Context
from cache.telegram_update_storage import TelegramUpdateRecord, TelegramUpdateStorage
from database.models import ChatAccess
from errors import ConfigError

from .base import BaseHandler
from .not_allowed import NotAllowedHandler


class SummarizeMessageHandler(BaseHandler):
    """
    Handles summarization commands by collecting recent chat history from Valkey and
    requesting a concise summary from the configured AI provider.
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
        self._logger = logging.getLogger(__name__)

    def can_handle(self, update: Update, context: Context, chat_settings: ChatAccess | None) -> bool:
        message = cast(Message, update.message)
        print(message.text)
        if not message.text or not message.text.startswith(self._SUMMARY_KEYWORDS):
            return False

        return self._COMMAND_PATTERN.match(message.text) is not None

    async def handle(self, update: Update, context: Context, chat_settings: ChatAccess | None) -> None:
        message = cast(Message, update.message)

        match = self._COMMAND_PATTERN.match(message.text)
        limit = int(match.group(2))
        if limit <= 0:
            await message.reply_text("Invalid limit. You must specify a positive number.")
            return None

        if limit > self._MAX_MESSAGES:
            limit = self._MAX_MESSAGES
            await message.reply_text(
                f"Limit is greater than the maximum allowed ({self._MAX_MESSAGES}). Using {limit}."
            )

        history = await self._retrieve_history(chat_id=int(chat_settings.chat_id), limit=limit)
        message_chain = await self._collect_reply_chain(history, context.bot)
        ai_client = self._resolve_ai_client(chat_settings)
        response = await ai_client.answer(message_chain)
        await message.reply_text(response)
        return None

    async def _collect_reply_chain(
        self, messages: Sequence[TelegramUpdateRecord], bot: Bot
    ) -> Sequence[tuple[str, str]]:
        is_bot_message = partial(self._is_same_user, bot)
        result: list[tuple[str, str]] = [
            (
                "system",
                "You are a helpful friend to assist. You need to go through the messages of the conversation "
                "and summarize in general what has been discussed. Do not make up your own ideas. Be concise. "
                "Do not include any personal opinion until you directly asked.",
            )
        ]
        for message in messages:
            if not message.message_text:
                continue
            if is_bot_message(message.user_id):
                result.append(("assistant", message.message_text))
            else:
                result.append((message.username, message.message_text))
        return result

    def _is_same_user(self, user1: User | Bot | int, user2: User | Bot | int) -> bool:
        user1_id = user1.id if isinstance(user1, User | Bot) else user1
        user2_id = user2.id if isinstance(user2, User | Bot) else user2
        return user1_id == user2_id

    async def _retrieve_history(self, chat_id: int, limit: int) -> list[TelegramUpdateRecord]:
        return await self._update_storage.get_last_messages(chat_id=chat_id, limit=limit)

    def _resolve_ai_client(self, record: ChatAccess) -> BaseAiClient:
        provider = record.provider or ChatAccess.DEFAULT_PROVIDER
        if not self._ai_registry.contains(provider):
            raise ConfigError(f"AI provider '{provider}' is not registered.")
        return self._ai_registry.get(provider)

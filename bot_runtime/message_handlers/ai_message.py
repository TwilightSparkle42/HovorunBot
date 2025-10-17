from functools import partial
from typing import Sequence, cast

from injector import Inject
from telegram import Bot, Message, Update, User

from ai_client.base import AiClientRegistry, BaseAiClient
from bot_types import Context
from database.models import ChatAccess
from errors import ConfigError
from settings.bot import TelegramSettings

from .base import BaseHandler


class AiMessageHandler(BaseHandler):
    def __init__(self, ai_registry: Inject[AiClientRegistry], bot_settings: Inject[TelegramSettings]) -> None:
        self._ai_registry = ai_registry
        self._bot_settings = bot_settings

    def can_handle(self, update: Update, context: Context, chat_settings: ChatAccess | None) -> bool:
        message = cast(Message, update.message)
        text = update.message.text
        if self._bot_settings.telegram_bot_name in text:
            return True
        reply_to = message.reply_to_message
        return bool(reply_to and reply_to.from_user and self._is_same_user(reply_to.from_user, context.bot))

    async def handle(self, update: Update, context: Context, chat_settings: ChatAccess | None) -> bool:
        assert chat_settings is not None, "Chat access record is required."
        message = cast(Message, update.message)
        message_chain = await self._collect_reply_chain(update, context.bot)
        ai_client = self._resolve_ai_client(chat_settings)
        answer = await ai_client.answer(message_chain)
        await message.reply_text(answer)
        return True

    def _resolve_ai_client(self, record: ChatAccess) -> BaseAiClient:
        provider = record.provider or ChatAccess.DEFAULT_PROVIDER
        if not self._ai_registry.contains(provider):
            raise ConfigError(f"AI provider '{provider}' is not registered.")
        return self._ai_registry.get(provider)

    async def _collect_reply_chain(self, update: Update, bot: Bot) -> Sequence[tuple[str, str]]:
        message = cast(Message, update.message)
        result: list[tuple[str, str]] = []
        is_bot_message = partial(self._is_same_user, bot)
        if is_bot_message(message.from_user):
            result.append(("assistant", message.text or ""))
        else:
            result.append((message.from_user.name, message.text or ""))
        current_message = message
        while current_message.reply_to_message:
            reply = current_message.reply_to_message
            if not reply:
                break
            if is_bot_message(reply.from_user):
                result.append(("assistant", reply.text or ""))
            else:
                result.append((reply.from_user.name, reply.text or ""))
            current_message = reply
        return result

    def _is_same_user(self, user1: User | Bot, user2: User | Bot) -> bool:
        return user1.id == user2.id

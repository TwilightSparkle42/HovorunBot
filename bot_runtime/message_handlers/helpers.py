from __future__ import annotations

from datetime import datetime, timezone
from typing import Callable, Sequence

from telegram import Bot, Message, User

from ai_client.base import AiClientRegistry, BaseAiClient
from cache.telegram_update_storage import TelegramUpdateRecord
from database.models import ChatAccess
from errors import ConfigError

UserLike = User | Bot | int


def resolve_ai_client(registry: AiClientRegistry, record: ChatAccess) -> BaseAiClient:
    """
    Return an AI client for the chat record or raise a concise configuration error.
    Keeping this in a helper avoids repeating provider resolution logic in handlers.
    """
    provider = record.provider or ChatAccess.DEFAULT_PROVIDER
    if not registry.contains(provider):
        raise ConfigError(f"AI provider '{provider}' is not registered.")
    return registry.get(provider)


def user_id(user: UserLike) -> int:
    """Return a stable identifier for a Telegram user, bot, or raw id."""
    if isinstance(user, (User, Bot)):
        return user.id
    return int(user)


def is_same_user(left: UserLike, right: UserLike) -> bool:
    """Loose equality helper that accounts for raw identifiers and telegram objects."""
    return user_id(left) == user_id(right)


def build_message_chain(
    records: Sequence[TelegramUpdateRecord],
    bot: Bot,
    *,
    prefix: Sequence[tuple[str, str]] | None = None,
) -> list[tuple[str, str]]:
    """
    Convert chat messages into a sequence formatted for AI providers.
    """

    def is_bot(user: UserLike) -> bool:
        return is_same_user(bot, user)

    result: list[tuple[str, str]] = list(prefix) if prefix else []
    for record in records:
        append_record_message(result, record=record, is_bot=is_bot)
    return result


def reply_chain_to_records(message: Message) -> list[TelegramUpdateRecord]:
    """
    Convert a Telegram message and its reply chain into ordered TelegramUpdateRecord objects (newest first).
    """
    result: list[TelegramUpdateRecord] = []
    current: Message | None = message
    fallback_update_id = message.message_id or 0
    offset = 0
    while current is not None:
        record = _message_to_record(current, fallback_update_id=fallback_update_id + offset)
        result.append(record)
        current = current.reply_to_message
        offset += 1
    return result


def append_record_message(
    result: list[tuple[str, str]], *, record: TelegramUpdateRecord, is_bot: Callable[[UserLike], bool]
) -> None:
    """
    Append a cached telegram record to ``result`` if it contains text, tagging bot-originated messages as ``assistant``.
    """
    text = record.message_text
    if not text:
        return

    author_id = record.user_id
    if author_id is not None and is_bot(author_id):
        role = "assistant"
    else:
        role = _resolve_username(author_id, record.username, record.author, record)

    result.append((role, text))


def _resolve_username(
    author: UserLike | None,
    username_hint: str | None,
    author_hint: str | None,
    record: TelegramUpdateRecord | None = None,
) -> str:
    if username_hint:
        return username_hint
    if author_hint:
        return author_hint
    if isinstance(author, (User, Bot)):
        for attr in ("full_name", "name", "first_name", "username"):
            candidate = getattr(author, attr, None)
            if candidate:
                return candidate
    if author is not None:
        return str(author)
    if record and record.user_id is not None:
        return str(record.user_id)
    return "Unknown"


def _message_to_record(message: Message, *, fallback_update_id: int) -> TelegramUpdateRecord:
    """
    Build an in-memory TelegramUpdateRecord from a live Telegram message object.
    """
    user = message.from_user
    chat = message.chat
    message_date = _normalize_datetime(message.date)

    return TelegramUpdateRecord(
        update_id=fallback_update_id,
        message_id=message.message_id,
        chat_id=chat.id if chat else None,
        chat_type=chat.type if chat else None,
        message_text=_extract_message_text(message),
        user_id=user.id if user else None,
        username=user.username if user else None,
        author=user.full_name if user else None,
        first_name=user.first_name if user else None,
        last_name=user.last_name if user else None,
        language_code=getattr(user, "language_code", None) if user else None,
        message_date=message_date,
        received_at=datetime.now(timezone.utc),
    )


def _normalize_datetime(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


def _extract_message_text(message: Message) -> str | None:
    """Return textual content from a Telegram message, falling back to the media caption."""
    if message.text:
        return message.text
    if message.caption:
        return message.caption
    return None


__all__ = [
    "resolve_ai_client",
    "user_id",
    "is_same_user",
    "build_message_chain",
    "reply_chain_to_records",
]

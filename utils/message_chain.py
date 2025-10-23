from datetime import datetime, timezone
from typing import Any, Callable, Sequence

from telegram import Bot, Message, User

from ai_client.base import AiClientRegistry, AiMessage, AiRole, BaseAiClient
from cache.telegram_update_storage import TelegramUpdateRecord
from database.models import ChatConfiguration
from errors import ConfigError

UserLike = User | Bot | int

__all__ = [
    "resolve_ai_client",
    "user_id",
    "is_same_user",
    "build_message_chain",
    "reply_chain_to_records",
]


def resolve_ai_client(registry: AiClientRegistry, record: ChatConfiguration) -> BaseAiClient[Any]:
    """
    Resolve an AI client for the supplied chat record.

    :param registry: Registry holding available AI client instances.
    :param record: Chat configuration specifying the desired provider.
    :raises ConfigError: If the configured provider is not registered.
    :returns: The AI client bound to the chat's provider.
    """
    model_configuration = record.model_configuration
    if model_configuration is None:
        raise ConfigError("Chat has no model configuration attached.")

    model = model_configuration.model
    provider = model.provider
    if provider is None:
        raise ConfigError("Configured model has no provider assigned.")

    provider_name = provider.name
    if not registry.contains(provider_name):
        raise ConfigError(f"AI provider '{provider_name}' is not registered.")
    return registry.get(provider_name)


def user_id(user: UserLike) -> int:
    """
    Return a stable identifier for a Telegram user, bot, or raw identifier.

    :param user: Telegram ``User``/``Bot`` instance or numeric identifier.
    :returns: Integer identifier for the user.
    """
    if isinstance(user, (User, Bot)):
        return user.id
    return int(user)


def is_same_user(left: UserLike, right: UserLike) -> bool:
    """
    Compare two user references while accounting for Telegram objects versus raw identifiers.

    :param left: First user reference.
    :param right: Second user reference.
    :returns: ``True`` when both references resolve to the same identifier.
    """
    return user_id(left) == user_id(right)


def build_message_chain(
    records: Sequence[TelegramUpdateRecord],
    bot: Bot,
    *,
    prefix: Sequence[AiMessage] | None = None,
) -> list[AiMessage]:
    """
    Convert chat messages into a sequence of :class:`AiMessage` entries suitable for AI providers.

    :param records: Cached Telegram updates ordered from newest to oldest.
    :param bot: Telegram bot instance used to detect assistant messages.
    :param prefix: Optional conversation prefix to prepend to the chain.
    :returns: A list of :class:`AiMessage`.
    """

    def is_bot(user: UserLike) -> bool:
        return is_same_user(bot, user)

    result: list[AiMessage] = list(prefix) if prefix else []
    for record in records:
        message = _record_to_message(record=record, is_bot=is_bot)
        if message is not None:
            result.append(message)
    return result


def reply_chain_to_records(message: Message) -> list[TelegramUpdateRecord]:
    """
    Convert a message and its reply chain into cached record instances.

    :param message: Telegram message whose ancestry should be traversed.
    :returns: Records ordered from newest to oldest covering the reply loop.
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


def _record_to_message(
    *,
    record: TelegramUpdateRecord,
    is_bot: Callable[[UserLike], bool],
) -> AiMessage | None:
    text = record.message_text
    if not text:
        return None

    author_id = record.user_id
    if author_id is not None and is_bot(author_id):
        return AiMessage(role=AiRole.ASSISTANT, content=text)

    username = _resolve_username(author_id, record.username, record.author, record)
    return AiMessage(role=AiRole.USER, content=text, name=username)


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
            if isinstance(candidate, str) and candidate:
                return candidate
    if author is not None:
        return str(author)
    if record and record.user_id is not None:
        return str(record.user_id)
    return "Unknown"


def _message_to_record(message: Message, *, fallback_update_id: int) -> TelegramUpdateRecord:
    """
    Build an in-memory :class:`TelegramUpdateRecord` from a live Telegram message.

    :param message: Telegram message to convert.
    :param fallback_update_id: Identifier to use when the original update id is unknown.
    :returns: A synthetic cached record representing the message.
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
    """
    Extract textual content from a Telegram message, falling back to the caption.

    :param message: Telegram message to inspect.
    :returns: Message text or caption if available; otherwise ``None``.
    """
    if message.text:
        return message.text
    if message.caption:
        return message.caption
    return None

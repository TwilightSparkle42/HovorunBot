from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Final

from injector import Inject
from pydantic import BaseModel
from telegram import Chat, Message, Update, User

from cache.valkey import ValkeyCache


class TelegramUpdateRecord(BaseModel):
    update_id: int
    message_id: int | None = None
    chat_id: int | None = None
    chat_type: str | None = None
    message_text: str | None = None
    user_id: int | None = None
    username: str | None = None
    author: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    language_code: str | None = None
    message_date: datetime | None = None
    received_at: datetime

    @property
    def redis_key(self) -> str:
        return f"telegram:update:{self.update_id}"


class TelegramUpdateStorage:
    """Persist incoming telegram updates into Valkey with a 24-hour TTL."""

    _TTL: Final[int] = int(timedelta(hours=24).total_seconds())

    _MAX_HISTORY_FETCH: Final[int] = 200

    def __init__(self, cache: Inject[ValkeyCache]) -> None:
        self._client = cache.client
        self._logger = logging.getLogger(__name__)

    async def store(self, update: Update) -> None:
        """Persist the incoming update as JSON in Valkey."""
        record = self._build_record(update)
        if record is None:
            return

        payload = record.model_dump_json()

        try:
            await self._client.set(name=record.redis_key, value=payload, ex=self._TTL)
            if record.chat_id is not None:
                await self._index_update(record)
            self._logger.debug("Stored telegram update %s in cache", record.update_id)
        except Exception as exc:
            self._logger.warning("Failed to store telegram update %s: %s", record.update_id, exc)

    async def get_last_messages(
        self,
        chat_id: int,
        limit: int,
        *,
        exclude_update_id: int | None = None,
    ) -> list[TelegramUpdateRecord]:
        """
        Fetch up to ``limit`` most recent telegram updates for the given chat,
        excluding the provided update ID if supplied.
        """
        if limit <= 0:
            return []

        chat_key = self._chat_updates_key(chat_id)
        fetch_count = min(limit, self._MAX_HISTORY_FETCH)
        try:
            raw_update_ids = await self._client.zrevrange(chat_key, 0, fetch_count - 1)
        except Exception as exc:
            self._logger.warning("Failed to fetch cached updates for chat %s: %s", chat_id, exc)
            return []

        records: list[TelegramUpdateRecord] = []

        for raw_id in raw_update_ids:
            try:
                update_id = int(raw_id)
            except (TypeError, ValueError):
                continue
            if exclude_update_id is not None and update_id == exclude_update_id:
                continue

            payload = await self._client.get(self._record_key(update_id))
            if payload is None:
                continue
            try:
                record = TelegramUpdateRecord.model_validate_json(payload)
            except Exception as exc:  # noqa: BLE001 - log and skip malformed payloads
                self._logger.debug("Failed to parse cached update %s: %s", update_id, exc)
                continue

            records.append(record)
            if len(records) >= limit:
                break

        return records

    def _build_record(self, update: Update) -> TelegramUpdateRecord | None:
        message: Message | None = update.effective_message
        user: User | None = update.effective_user
        chat: Chat | None = update.effective_chat

        if update.update_id is None:
            return None

        message_date = message.date if message and message.date else None
        if message_date is not None and message_date.tzinfo is None:
            message_date = message_date.replace(tzinfo=timezone.utc)

        received_at = datetime.now(timezone.utc)

        return TelegramUpdateRecord(
            update_id=update.update_id,
            message_id=message.message_id if message else None,
            chat_id=chat.id if chat else None,
            chat_type=chat.type if chat else None,
            message_text=self._extract_text(message),
            user_id=user.id if user else None,
            username=user.username if user else None,
            author=user.full_name if user else None,
            first_name=user.first_name if user else None,
            last_name=user.last_name if user else None,
            language_code=user.language_code if user and hasattr(user, "language_code") else None,
            message_date=message_date,
            received_at=received_at,
        )

    @staticmethod
    def _extract_text(message: Message | None) -> str | None:
        if message is None:
            return None
        if message.text:
            return message.text
        if message.caption:
            return message.caption
        return None

    @staticmethod
    def _chat_updates_key(chat_id: int) -> str:
        return f"telegram:chat:{chat_id}:updates"

    @staticmethod
    def _record_key(update_id: int) -> str:
        return f"telegram:update:{update_id}"

    async def _index_update(self, record: TelegramUpdateRecord) -> None:
        """
        Index a stored update in a per-chat sorted set for efficient history lookups.
        """
        chat_id = record.chat_id
        if chat_id is None:
            return
        chat_key = self._chat_updates_key(chat_id)
        try:
            await self._client.zadd(chat_key, {str(record.update_id): record.received_at.timestamp()})
            await self._client.expire(chat_key, self._TTL)
        except Exception as exc:
            self._logger.debug(
                "Failed to index telegram update %s for chat %s: %s",
                record.update_id,
                record.chat_id,
                exc,
            )


__all__ = ["TelegramUpdateRecord", "TelegramUpdateStorage"]

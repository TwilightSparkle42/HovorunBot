from __future__ import annotations

from injector import Inject
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from database.models import ChatAccess


class ChatAccessRepository:
    """
    Persistence helper for chat access records.

    The repository coordinates asynchronous session management for CRUD operations on
    :class:`database.models.ChatAccess`.
    """

    def __init__(self, session_factory: Inject[async_sessionmaker[AsyncSession]]) -> None:
        self._session_factory = session_factory

    async def ensure_exists(self, chat_id: str) -> ChatAccess | None:
        """
        Fetch an existing record or create a new denied-by-default entry.

        :param chat_id: Identifier of the chat requesting access.
        :returns: The persisted :class:`ChatAccess` row or ``None`` if the lookup fails after conflict handling.
        """
        async with self._session_factory() as session:
            instance = await self._get_by_chat_id(session, chat_id)
            if instance is not None:
                return instance

            instance = ChatAccess(chat_id=chat_id, provider=ChatAccess.DEFAULT_PROVIDER)
            session.add(instance)

            try:
                await session.commit()
            except IntegrityError:
                await session.rollback()
                return await self._get_by_chat_id(session, chat_id)

            await session.refresh(instance)
            return instance

    async def is_allowed(self, chat_id: str) -> bool:
        """
        Determine whether a chat has been granted access.

        :param chat_id: Identifier of the chat requesting access.
        :returns: ``True`` when the chat is authorised; otherwise ``False``.
        """
        async with self._session_factory() as session:
            record = await self._get_by_chat_id(session, chat_id)
            return bool(record and record.allowed)

    async def _get_by_chat_id(self, session: AsyncSession, chat_id: str) -> ChatAccess | None:
        result = await session.execute(select(ChatAccess).where(ChatAccess.chat_id == chat_id))
        return result.scalar_one_or_none()

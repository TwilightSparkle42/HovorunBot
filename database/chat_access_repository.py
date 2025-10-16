from __future__ import annotations

from injector import Inject
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from database.models import ChatAccess


class ChatAccessRepository:
    """Persistence helper for chat access records."""

    def __init__(self, session_factory: Inject[sessionmaker[Session]]) -> None:
        self._session_factory = session_factory

    def ensure_exists(self, chat_id: str) -> ChatAccess:
        """Return an existing record or create a new denied-by-default entry."""
        with self._session_factory() as session:
            instance = self._get_by_chat_id(session, chat_id)
            if instance is not None:
                return instance

            instance = ChatAccess(chat_id=chat_id)
            session.add(instance)

            try:
                session.commit()
            except IntegrityError:
                session.rollback()
                return self._get_by_chat_id(session, chat_id)

            session.refresh(instance)
            return instance

    def is_allowed(self, chat_id: str) -> bool:
        """Check whether a chat has been granted access."""
        with self._session_factory() as session:
            record = self._get_by_chat_id(session, chat_id)
            return bool(record and record.allowed)

    def _get_by_chat_id(
        self, session: Session, chat_id: str
    ) -> ChatAccess | None:
        return session.execute(
            select(ChatAccess).where(ChatAccess.chat_id == chat_id)
        ).scalar_one_or_none()

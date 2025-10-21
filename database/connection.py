from __future__ import annotations

from injector import Inject
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from settings.database import DatabaseSettings


class DatabaseConnection:
    """
    Manage the shared SQLAlchemy async engine and session factory for the application.

    The connection settings originate from :class:`settings.database.DatabaseSettings`.
    """

    def __init__(self, settings: Inject[DatabaseSettings]) -> None:
        self._settings = settings
        self._engine = self._create_engine()
        self._session_factory = self._create_session_factory()

    @property
    def engine(self) -> AsyncEngine:
        return self._engine

    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        return self._session_factory

    def _create_engine(self) -> AsyncEngine:
        """
        Instantiate the SQLAlchemy async engine.

        :returns: Configured :class:`sqlalchemy.ext.asyncio.AsyncEngine` instance.
        """
        return create_async_engine(self._settings.sqlalchemy_async_url, future=True)

    def _create_session_factory(self) -> async_sessionmaker[AsyncSession]:
        """
        Create a session factory bound to the shared engine.

        :returns: Async session maker with commit expiry disabled.
        """
        return async_sessionmaker(
            bind=self._engine,
            expire_on_commit=False,
        )

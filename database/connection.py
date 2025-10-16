from __future__ import annotations

from injector import Inject
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from settings.database import DatabaseSettings


class DatabaseConnection:
    """
    Encapsulates the SQLAlchemy engine and session factory configuration.
    """

    def __init__(self, settings: Inject[DatabaseSettings]) -> None:
        self._settings = settings
        self._engine = self._create_engine()
        self._session_factory = self._create_session_factory()

    @property
    def engine(self) -> Engine:
        return self._engine

    @property
    def session_factory(self) -> sessionmaker[Session]:
        return self._session_factory

    def _create_engine(self) -> Engine:
        """
        Create a SQLAlchemy engine using the configured database settings.
        """
        return create_engine(self._settings.sqlalchemy_url, future=True)

    def _create_session_factory(self) -> sessionmaker[Session]:
        """
        Create a session factory bound to the engine.
        """
        return sessionmaker(
            bind=self._engine,
            class_=Session,
            expire_on_commit=False,
        )

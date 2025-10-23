from typing import Any, cast

from injector import Inject
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import ORMExecuteState, Session, with_loader_criteria

from database.base import DeletableMixin
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
        session_factory = async_sessionmaker(
            bind=self._engine,
            expire_on_commit=False,
        )
        self._register_session_listeners(session_factory)
        return session_factory

    @staticmethod
    def _register_session_listeners(session_factory: async_sessionmaker[AsyncSession]) -> None:
        """
        Attach event listeners to implement application-wide behaviours for ORM sessions.

        Listeners handle soft-delete semantics and ensure deleted rows are hidden from default queries.
        """

        sync_session_class = cast(
            type[Session],
            getattr(session_factory, "sync_session_class", Session),
        )

        @event.listens_for(sync_session_class, "before_flush", propagate=True)
        def _handle_soft_delete(session: Session, flush_context: Any, _instances: Any) -> None:
            del flush_context, _instances
            for instance in list(session.deleted):
                if isinstance(instance, DeletableMixin):
                    instance.mark_deleted()
                    session.add(instance)
                    session.deleted.discard(instance)

        @event.listens_for(sync_session_class, "do_orm_execute", propagate=True)
        def _filter_deleted(execute_state: ORMExecuteState) -> None:
            if not execute_state.is_select or execute_state.execution_options.get("include_deleted", False):
                return

            execute_state.statement = execute_state.statement.options(
                with_loader_criteria(
                    DeletableMixin,
                    lambda cls: cls.deleted.is_(False),
                    include_aliases=True,
                )
            )

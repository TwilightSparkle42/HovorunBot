from injector import Binder, Module, provider, singleton
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from database.chat_configuration_repository import ChatConfigurationRepository
from database.connection import DatabaseConnection


class DatabaseModule(Module):
    """
    Configure database-related bindings for dependency injection.

    Exposes the shared :class:`database.connection.DatabaseConnection`, repository, engine, and session factory.
    """

    def configure(self, binder: Binder) -> None:
        binder.bind(DatabaseConnection, to=DatabaseConnection, scope=singleton)
        binder.bind(ChatConfigurationRepository, to=ChatConfigurationRepository, scope=singleton)

    @provider
    @singleton
    def provide_async_engine(self, connection: DatabaseConnection) -> AsyncEngine:
        return connection.engine

    @provider
    @singleton
    def provide_session_factory(self, connection: DatabaseConnection) -> async_sessionmaker[AsyncSession]:
        return connection.session_factory

from injector import Binder, Module, provider, singleton
from sqlalchemy import Engine
from sqlalchemy.orm import Session, sessionmaker

from database.chat_access_repository import ChatAccessRepository
from database.connection import DatabaseConnection


class DatabaseModule(Module):
    """Registers database infrastructure with the injector."""

    def configure(self, binder: Binder) -> None:
        binder.bind(DatabaseConnection, to=DatabaseConnection, scope=singleton)
        binder.bind(ChatAccessRepository, to=ChatAccessRepository, scope=singleton)

    @provider
    @singleton
    def provide_engine(self, connection: DatabaseConnection) -> Engine:
        return connection.engine

    @provider
    @singleton
    def provide_session_factory(self, connection: DatabaseConnection) -> sessionmaker[Session]:
        return connection.session_factory

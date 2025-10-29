from injector import Injector

from database.connection import DatabaseConnection
from di_config import get_injector

__all__ = [
    "DEFAULT_READONLY_FIELDS",
    "session_factory",
]

injector: Injector = get_injector()
database_connection = injector.get(DatabaseConnection)

session_factory = database_connection.session_maker

DEFAULT_READONLY_FIELDS: tuple[str, ...] = (
    "id",
    "deleted",
    "deleted_on",
    "created_at",
    "updated_at",
)

import os
from pathlib import Path

from pydantic import field_validator

from .base import SettingsBase


class DatabaseSettings(SettingsBase):
    """
    Configuration for the application's relational database.

    SQLite (via ``sqlite+aiosqlite``) is the only supported backend at the moment; alternative databases are rejected.
    The ``DATABASE_URL`` environment variable, when present, must already point to an async SQLite DSN and takes
    precedence over ``DATABASE_PATH``. When both variables are supplied, ``DATABASE_URL`` wins and the path value is
    ignored. If neither is provided, a default SQLite database is created at ``database_path`` relative to the project
    root.
    """

    class Config:
        env_file = os.environ.get("DATABASE_DOT_ENV", ".env")

    database_url: str | None = None
    database_path: Path = Path("askbro.db")

    @property
    def sqlalchemy_async_url(self) -> str:
        """
        Return the async SQLAlchemy connection URL, always using ``sqlite+aiosqlite``.

        :returns: Async SQLAlchemy DSN suitable for :func:`sqlalchemy.ext.asyncio.create_async_engine`.
        """
        if self.database_url:
            return self.database_url
        db_path = self.database_path.expanduser().resolve()
        return f"sqlite+aiosqlite:///{db_path}"

    @field_validator('database_url')
    @classmethod
    def _validate_async_sqlite(cls, value: str | None) -> str | None:
        """
        Ensure provided DSNs already target the async SQLite driver.

        :param value: Custom database URL read from configuration.
        :returns: The validated connection string or ``None`` when unspecified.
        :raises ValueError: If the URL does not use ``sqlite+aiosqlite``.
        """
        if value is None:
            return None
        if not value.startswith('sqlite+aiosqlite://'):
            raise ValueError('database_url must use the sqlite+aiosqlite driver')
        return value

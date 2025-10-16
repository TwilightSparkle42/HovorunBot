import os
from pathlib import Path

from .base import SettingsBase


class DatabaseSettings(SettingsBase):
    """Configuration for the application's relational database."""

    class Config:
        env_file = os.environ.get("DATABASE_DOT_ENV", ".env")

    database_url: str | None = None
    database_path: Path = Path("askbro.db")

    @property
    def sqlalchemy_url(self) -> str:
        """Return the SQLAlchemy connection URL, preferring explicit URLs."""
        if self.database_url:
            return self.database_url
        # Ensure absolute path so Alembic resolves the same location everywhere.
        db_path = self.database_path.expanduser().resolve()
        return f"sqlite:///{db_path}"

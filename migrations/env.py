from __future__ import annotations

from logging.config import fileConfig

from alembic import context
from sqlalchemy import Engine

from database.base import BaseModel
from database.models import ChatAccess  # noqa: F401
from di_config import setup_di
from settings.database import DatabaseSettings

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = BaseModel.metadata


def _get_database_settings() -> DatabaseSettings:
    injector = setup_di()
    return injector.get(DatabaseSettings)


def _get_engine() -> Engine:
    injector = setup_di()
    engine = injector.get(Engine)
    config.set_main_option("sqlalchemy.url", str(engine.url))
    return engine


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    settings = _get_database_settings()
    context.configure(
        url=str(settings.sqlalchemy_url),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    engine = _get_engine()
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

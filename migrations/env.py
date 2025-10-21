from __future__ import annotations

import asyncio
import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import AsyncEngine

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from database.base import BaseModel  # noqa: E402
from di_config import setup_di  # noqa: E402
from settings.database import DatabaseSettings  # noqa: E402

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = BaseModel.metadata


def _get_database_settings() -> DatabaseSettings:
    injector = setup_di()
    return injector.get(DatabaseSettings)


def _get_async_engine() -> AsyncEngine:
    injector = setup_di()
    engine = injector.get(AsyncEngine)
    config.set_main_option("sqlalchemy.url", str(engine.url))
    return engine


def run_migrations_offline() -> None:
    """
    Execute migrations in offline mode.

    Alembic emits SQL statements without establishing a live database connection.
    """
    settings = _get_database_settings()
    context.configure(
        url=str(settings.sqlalchemy_async_url),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """
    Execute migrations in online mode.

    Alembic opens an async engine connection and applies schema changes directly.
    """
    engine = _get_async_engine()
    async with engine.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())

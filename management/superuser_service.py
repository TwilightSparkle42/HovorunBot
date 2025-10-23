import asyncio
import secrets
from dataclasses import dataclass

import bcrypt
from injector import Inject
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from database.connection import DatabaseConnection
from database.models.base import BaseModel
from database.models.user import User


@dataclass(slots=True)
class SuperuserCreationResult:
    """Result of the superuser creation routine.

    Attributes:
        created: Whether a new superuser was created.
        username: The superuser username.
        password: The generated plaintext password if created, otherwise None.
    """

    created: bool
    username: str
    password: str | None


class SuperuserCreator:
    """Create the first superuser in the database if it doesn't exist.

    Uses the app's async SQLAlchemy engine/session via DI.
    """

    def __init__(self, database: Inject[DatabaseConnection]) -> None:
        self._session_factory: async_sessionmaker[AsyncSession] = database.session_factory
        self._engine: AsyncEngine = database.engine

    async def _ensure_schema(self) -> None:
        """Ensure database schema exists (SQLite only; safe for first-run setup)."""
        async with self._engine.begin() as conn:
            await conn.run_sync(BaseModel.metadata.create_all)

    async def create_first_superuser(self, username: str = "admin") -> SuperuserCreationResult:
        """Create the first superuser if not present.

        Returns a result with generated password if created; otherwise, indicates existing superuser.
        """
        await self._ensure_schema()
        async with self._session_factory() as session:
            existing = await self._find_existing_superuser(session)
            if existing is not None:
                return SuperuserCreationResult(created=False, username=existing.username, password=None)

            password = self._generate_password()
            hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
            user = User(username=username, hash_password=hashed, is_active=True, is_superuser=True)
            session.add(user)
            await session.commit()
            return SuperuserCreationResult(created=True, username=username, password=password)

    async def _find_existing_superuser(self, session: AsyncSession) -> User | None:
        stmt = select(User).where(User.is_superuser.is_(True))
        result = await session.scalars(stmt)
        return result.first()

    @staticmethod
    def _generate_password() -> str:
        # 24 characters URL-safe random password (approx 144 bits of entropy)
        return secrets.token_urlsafe(18)


def create_superuser_sync(creator: SuperuserCreator, username: str = "admin") -> SuperuserCreationResult:
    """Convenience wrapper to run from synchronous CLI entrypoints."""
    return asyncio.run(creator.create_first_superuser(username=username))

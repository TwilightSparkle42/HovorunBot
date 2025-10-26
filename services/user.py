from typing import Self
from uuid import UUID

from injector import inject, provider, singleton
from sqlalchemy import Select, select

from database.connection import DatabaseConnection
from database.dtos.user import UserCredentials
from database.models import User


class UserService:
    @inject
    def __init__(self, db_connection: DatabaseConnection) -> None:
        self._db_connection = db_connection

    @classmethod
    @provider
    @singleton
    def build(cls, db_connection: DatabaseConnection) -> Self:
        return cls(db_connection)

    async def find_by_username(self, username: str) -> UserCredentials | None:
        selection = select(User).where(User.username == username)
        return await self._find_one(selection)

    async def find_by_id(self, user_id: UUID) -> UserCredentials | None:
        selection = select(User).where(User.id == user_id)
        return await self._find_one(selection)

    async def _find_one(self, selection: Select[tuple[User]]) -> UserCredentials | None:
        async with self._db_connection.session_maker() as session:
            result = await session.execute(selection)
            user = result.scalar_one_or_none()
            if user is None:
                return None
            return UserCredentials.from_user(user)

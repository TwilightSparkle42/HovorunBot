from typing import Self
from uuid import UUID

from pydantic import BaseModel

from database.models import User


class UserCredentials(BaseModel):
    """Lightweight view of a stored user credential record."""

    id: UUID
    username: str
    hash_password: str
    is_active: bool
    is_superuser: bool

    @classmethod
    def from_user(cls, user: User) -> Self:
        return cls(
            id=user.id,
            username=user.username,
            hash_password=user.hash_password,
            is_active=user.is_active,
            is_superuser=user.is_superuser,
        )

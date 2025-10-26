"""Authentication helpers for the admin panel."""

from typing import Self
from uuid import UUID

import bcrypt
from injector import inject, provider, singleton

from database.dtos.user import UserCredentials
from services.user import UserService


class AuthenticationError(RuntimeError):
    """Raised when authentication cannot complete successfully."""


class AuthenticationService:
    """Validate user credentials and expose helpers for session-aware operations."""

    @inject
    def __init__(self, user_service: UserService) -> None:
        self._user_service = user_service

    @classmethod
    @provider
    @singleton
    def build(cls, user_service: UserService) -> Self:
        return cls(user_service)

    async def authenticate(self, username: str, password: str) -> UserCredentials:
        """Validate provided credentials against stored user records."""
        user = await self._user_service.find_by_username(username)
        if user is None:
            raise AuthenticationError("Invalid username or password.")
        if not user.is_active:
            raise AuthenticationError("Account is inactive.")
        if not self._verify_password(password, user.hash_password):
            raise AuthenticationError("Invalid username or password.")
        return user

    async def get_user(self, user_id: UUID | str) -> UserCredentials | None:
        """Return the stored credentials for an authenticated principal."""
        if isinstance(user_id, str):
            user_id = UUID(user_id)
        return await self._user_service.find_by_id(user_id)

    def _verify_password(self, plaintext: str, hash_password: str) -> bool:
        try:
            return bcrypt.checkpw(plaintext.encode("utf-8"), hash_password.encode("utf-8"))
        except ValueError:
            return False

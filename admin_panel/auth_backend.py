"""Authentication backend integration for the SQLAdmin panel."""

from typing import Final

from fastapi import Request
from injector import Inject
from sqladmin.authentication import AuthenticationBackend

from services import AuthenticationError, AuthenticationService
from settings.admin import AdminSettings


class AdminPanelAuthBackend(AuthenticationBackend):
    """Authenticate SQLAdmin requests using the shared authentication service."""

    SESSION_USER_ID: Final[str] = "admin_user_id"
    SESSION_USERNAME: Final[str] = "admin_username"

    def __init__(self, service: Inject[AuthenticationService], settings: Inject[AdminSettings]) -> None:
        assert settings.secret_key is not None, "Secret key is required for authentication"
        super().__init__(secret_key=settings.secret_key)
        self._service = service

    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = str(form.get("username") or "").strip()
        password = form.get("password")
        if not username or not password:
            return False

        try:
            user = await self._service.authenticate(username=username, password=str(password))
        except AuthenticationError:
            return False

        request.session[self.SESSION_USER_ID] = user.id.hex
        request.session[self.SESSION_USERNAME] = user.username
        request.state.user = user
        return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        user_id = request.session.get(self.SESSION_USER_ID)
        if user_id is None:
            return False

        user = await self._service.get_user(user_id)
        if user is None or not user.is_active:
            request.session.clear()
            return False

        request.state.user = user
        return True

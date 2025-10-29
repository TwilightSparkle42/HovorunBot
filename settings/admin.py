import os
from importlib import import_module
from types import ModuleType
from typing import Self

from fastadmin.settings import Settings as FastAdminSettings  # type: ignore[import-untyped]
from injector import provider, singleton
from pydantic_settings import BaseSettings, SettingsConfigDict

from errors import ConfigError


class AdminSettings(BaseSettings):
    """
    Settings object for the admin panel interface.

    It is a mirror of the FastAdmin settings.
    """

    model_config = SettingsConfigDict(
        env_file=os.environ.get("ADMIN_DOT_ENV", ".env"),
        env_prefix="ADMIN_",
        extra="ignore",
    )
    prefix: str = "admin"
    site_name: str = "Hovorun Dashboard"
    site_sign_in_logo: str = "/admin/static/images/sign-in-logo.svg"
    site_header_logo: str = "/admin/static/images/header-logo.svg"
    site_favicon: str = "/admin/static/images/favicon.png"
    primary_color: str = "#009485"
    session_id_key: str = "admin_session_id"
    session_expired_at: int = 144000
    date_format: str = "YYYY-MM-DD"
    datetime_format: str = "YYYY-MM-DD HH:mm"
    time_format: str = "HH:mm:ss"
    user_model: str = "User"
    user_model_username_field: str = "username"
    secret_key: str | None = None
    disable_crop_image: bool = False

    def patch_fastadmin(self) -> None:
        FastAdminSettings.ADMIN_PREFIX = self.prefix
        FastAdminSettings.ADMIN_SITE_NAME = self.site_name
        FastAdminSettings.ADMIN_SITE_SIGN_IN_LOGO = self.site_sign_in_logo
        FastAdminSettings.ADMIN_SITE_HEADER_LOGO = self.site_header_logo
        FastAdminSettings.ADMIN_SITE_FAVICON = self.site_favicon
        FastAdminSettings.ADMIN_PRIMARY_COLOR = self.primary_color
        FastAdminSettings.ADMIN_SESSION_ID_KEY = self.session_id_key
        FastAdminSettings.ADMIN_SESSION_EXPIRED_AT = self.session_expired_at
        FastAdminSettings.ADMIN_DATE_FORMAT = self.date_format
        FastAdminSettings.ADMIN_DATETIME_FORMAT = self.datetime_format
        FastAdminSettings.ADMIN_TIME_FORMAT = self.time_format
        FastAdminSettings.ADMIN_USER_MODEL = self._get_fastadmin_model_name()
        FastAdminSettings.ADMIN_USER_MODEL_USERNAME_FIELD = self.user_model_username_field
        if not self.secret_key:
            raise ConfigError("Secret key is not configured")
        FastAdminSettings.ADMIN_SECRET_KEY = self.secret_key
        FastAdminSettings.ADMIN_DISABLE_CROP_IMAGE = self.disable_crop_image

    def _get_fastadmin_model_name(self) -> str:
        """
        Resolve the configured user model to the name FastAdmin expects.

        FastAdmin stores model registrations keyed by the class name, optionally prefixed by ``model_name_prefix``.
        To keep configuration flexible we accept fully qualified paths while returning the bare class name that matches
        our :class:`admin_panel.views.user.UserAdmin` registration.
        """
        configured = self.user_model.strip()
        if not configured:
            raise ConfigError("Admin user model is not configured")
        # Ensure FastAdmin model registrations are loaded before lookup.
        self._import_module("admin_panel.views.user")
        module_name, _, class_name = configured.rpartition(".")
        module = self._import_module(module_name or "database.models")
        if not hasattr(module, class_name):
            raise ConfigError(f"Cannot locate admin user model '{configured}'")
        return class_name

    @staticmethod
    def _import_module(module_name: str) -> ModuleType:
        try:
            return import_module(module_name)
        except ImportError as exc:
            raise ConfigError(f"Cannot import module '{module_name}' for admin configuration") from exc

    @classmethod
    @provider
    @singleton
    def build(cls) -> Self:
        result = cls()
        result.patch_fastadmin()
        return result

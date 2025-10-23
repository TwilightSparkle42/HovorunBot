from injector import Binder, Module, singleton

from .superuser_service import SuperuserCreator


class ManagementModule(Module):
    """DI registrations for management/operational services."""

    def configure(self, binder: Binder) -> None:  # noqa: D401 - short configure
        binder.bind(SuperuserCreator, to=SuperuserCreator, scope=singleton)

from injector import Binder, Module, singleton

from logging_config.configurator import configure_logging
from settings.logging import LoggingSettings


class LoggingModule(Module):
    """
    Configure the logging subsystem once the dependency injector is initialised.

    The module wires a singleton :class:`LoggingSettings` instance and applies the
    global logging configuration derived from it.
    """

    def configure(self, binder: Binder) -> None:
        settings = LoggingSettings()
        configure_logging(settings)
        binder.bind(LoggingSettings, to=settings, scope=singleton)

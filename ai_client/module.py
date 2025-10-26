from injector import Binder, Module, singleton

from .base import AiClientRegistry
from .grok import GrokAiClient


class AiClientModule(Module):
    """
    Configure dependency injection bindings for AI providers.

    Instantiates concrete AI clients and registers them within the shared registry.
    """

    def configure(self, binder: Binder) -> None:
        registry = AiClientRegistry()
        registry.register(GrokAiClient.get_name(), binder.injector.create_object(GrokAiClient))
        binder.bind(AiClientRegistry, to=registry, scope=singleton)

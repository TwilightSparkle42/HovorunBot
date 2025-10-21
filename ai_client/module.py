from injector import Binder, Module, singleton

from .base import AiClientRegistry
from .grok import GrokAiClient
from .infermatic import InfermaticAiClient


class AiClientModule(Module):
    """
    Configure dependency injection bindings for AI providers.

    Instantiates concrete AI clients and registers them within the shared registry.
    """

    def configure(self, binder: Binder) -> None:
        binder.bind(InfermaticAiClient, to=InfermaticAiClient, scope=singleton)
        binder.bind(GrokAiClient, to=GrokAiClient, scope=singleton)

        registry = AiClientRegistry()
        registry.register(InfermaticAiClient.get_name(), binder.injector.get(InfermaticAiClient))
        registry.register(GrokAiClient.get_name(), binder.injector.get(GrokAiClient))

        binder.bind(AiClientRegistry, to=registry, scope=singleton)

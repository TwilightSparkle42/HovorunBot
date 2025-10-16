from injector import Binder, Module, singleton

from .infermatic import InfermaticAiClient


class AiClientModule(Module):
    """Provides AI client bindings."""

    def configure(self, binder: Binder) -> None:
        binder.bind(InfermaticAiClient, to=InfermaticAiClient, scope=singleton)

from abc import ABC, abstractmethod

from pydantic_settings import BaseSettings


class BaseAiClient[TSettings: BaseSettings](ABC):
    def __init__(self, settings: TSettings) -> None:
        self._settings = settings

    @abstractmethod
    async def get_known_models(self) -> str:
        """Return a human-readable list of known models."""
        raise NotImplementedError

    @abstractmethod
    async def answer(self, message: str) -> str:
        """Answer a user message with a response from the AI model."""
        raise NotImplementedError

from abc import ABC, abstractmethod
from typing import Sequence

from pydantic_settings import BaseSettings

from utils.di import Registry


class BaseAiClient[TSettings: BaseSettings](ABC):
    def __init__(self, settings: TSettings) -> None:
        self._settings = settings

    @classmethod
    def get_name(cls) -> str:
        return cls.__name__.removesuffix("AiClient")

    @abstractmethod
    async def answer(self, message_chain: Sequence[tuple[str, str]]) -> str:
        """Answer a user message with a response from the AI model."""
        raise NotImplementedError


class AiClientRegistry(Registry[str, BaseAiClient]):
    def __init__(self) -> None:
        super().__init__(BaseAiClient)

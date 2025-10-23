from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING, Any, ClassVar, Sequence

from errors import ConfigError
from settings.ai_client.base_settings import GeneralAiSettings
from utils.di import Registry

from .model_params import BaseModelParams

if TYPE_CHECKING:
    from database.models import ModelConfiguration


class AiRole(StrEnum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


@dataclass(slots=True)
class AiMessage:
    role: AiRole
    content: str
    name: str | None = None

    def as_payload(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "role": self.role.value,
            "content": self.content,
        }
        if self.name:
            payload["name"] = self.name
        return payload


type MessageChain = Sequence[AiMessage]


class BaseAiClient[TSettings: GeneralAiSettings](ABC):
    PROVIDER_NAME: ClassVar[str | None] = None

    def __init__(self, settings: TSettings) -> None:
        self._settings = settings

    def build_model_params(self, model_config: ModelConfiguration | None) -> BaseModelParams:
        return BaseModelParams.build(
            model=self.resolve_model_name(model_config),
            system_message=self.resolve_system_message(model_config),
            settings=self._settings,
            model_config=model_config,
        )

    def resolve_model_name(self, model_config: ModelConfiguration | None) -> str:
        if model_config is None or model_config.model is None or model_config.model.name is None:
            default_model = self._settings.default_model
            if default_model is None:
                raise ConfigError(f"Default model is not configured for {self.__class__.__name__}.")
            return default_model
        return model_config.model.name

    def resolve_system_message(self, model_config: ModelConfiguration | None) -> str | None:
        if model_config is None:
            return self._settings.system_message
        if model_config.system_message is not None:
            return model_config.system_message
        return self._settings.system_message

    def build_messages(self, message_chain: MessageChain, model_config: ModelConfiguration | None) -> list[AiMessage]:
        chain = list(message_chain)
        return self.inject_system_messages(chain, model_config)

    def inject_system_messages(
        self,
        messages: list[AiMessage],
        model_config: ModelConfiguration | None,
    ) -> list[AiMessage]:
        """
        Hook for providers to add or alter system messages before dispatch.
        """

        system_message = self.resolve_system_message(model_config)
        if system_message:
            return [AiMessage(role=AiRole.SYSTEM, content=system_message), *messages]
        return list(messages)

    @classmethod
    def get_name(cls) -> str:
        if cls.PROVIDER_NAME is not None:
            return cls.PROVIDER_NAME.lower()
        return cls.__name__.removesuffix("AiClient").lower()

    @abstractmethod
    async def answer(
        self,
        message_chain: MessageChain,
        model_configuration: ModelConfiguration | None = None,
    ) -> str:
        """
        Generate a response to the supplied conversation history.

        :param message_chain: Sequence of :class:`AiMessage` representing the conversation so far.
        :param model_configuration: Configuration for the model to use. If not specified, the default configuration
            will be used.
        :returns: The assistant's reply text.
        """
        raise NotImplementedError


class AiClientRegistry(Registry[str, BaseAiClient[Any]]):
    def __init__(self) -> None:
        super().__init__(BaseAiClient)

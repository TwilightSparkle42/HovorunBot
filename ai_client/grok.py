import logging
from typing import TYPE_CHECKING, Any

from injector import Inject
from xai_sdk import AsyncClient  # type: ignore[import-untyped]
from xai_sdk.chat import assistant, system, user  # type: ignore[import-untyped]

from settings.ai_client.grok_settings import GrokSettings

from .base import AiMessage, AiRole, BaseAiClient, MessageChain
from .model_params import GrokModelParams

if TYPE_CHECKING:
    from database.models import ModelConfiguration


logger = logging.getLogger(__name__)


class GrokAiClient(BaseAiClient[GrokSettings]):
    def __init__(self, settings: Inject[GrokSettings]) -> None:
        super().__init__(settings)
        self._client: AsyncClient | None = None

    async def answer(
        self,
        message_chain: MessageChain,
        model_config: ModelConfiguration | None = None,
    ) -> str:
        params = self.build_model_params(model_config)
        grok_params = params.convert(GrokModelParams)
        grok_kwargs = grok_params.to_grok_kwargs()
        converted_messages = self.convert_messages(self.build_messages(message_chain, model_config))

        try:
            chat = self._get_client().chat.create(**grok_kwargs)
            for message in converted_messages:
                chat.append(message)
            response: Any = await chat.sample()
            return str(response.content)
        except Exception as error:  # noqa: BLE001 - TODO: resolve for specific errors later
            logger.exception("Grok API call failed")
            return str(error)

    def convert_messages(self, messages: list[AiMessage]) -> list[Any]:
        return [self.convert_message(message) for message in messages]

    def convert_message(self, message: AiMessage) -> Any:
        match message.role:
            case AiRole.SYSTEM:
                return system(message.content)
            case AiRole.ASSISTANT:
                return assistant(message.content)
            case AiRole.USER:
                if message.name:
                    return user(f"{message.name}: {message.content}")
                return user(message.content)
            case _:
                raise NotImplementedError("Unsupported AI message role for Grok conversion")

    def _get_client(self) -> AsyncClient:
        if self._client is None:
            api_key = self._settings.api_key
            if not api_key:
                msg = "Grok API key is not configured"
                raise ValueError(msg)
            self._client = AsyncClient(api_key=api_key, timeout=3600)
        return self._client

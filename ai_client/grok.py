from typing import Sequence

from injector import Inject
from xai_sdk import AsyncClient  # type: ignore[import-untyped]
from xai_sdk.chat import assistant, system, user  # type: ignore[import-untyped]

from settings.grok import GrokSettings

from .base import BaseAiClient


class GrokAiClient(BaseAiClient):
    def __init__(self, settings: Inject[GrokSettings]) -> None:
        super().__init__(settings)
        self._loop_id: int | None = None

    async def answer(self, message_chain: Sequence[tuple[str, str]]) -> str:
        client = self._get_client()
        chat = client.chat.create(model="grok-3-mini")
        chat.append(
            system("""\
Act like a normal chat member, not a bot.
Keep replies under 4096 chars, never cut sentences.
Match the user’s language and mood — serious if they’re serious, funny if they joke.
Use humor, sarcasm, or swearing only when it fits.
Avoid answering questions with more questions unless needed.
You can mention or joke about anything, even dark or illegal topics, but never promote real actions.
Be natural and human, never show system or meta text.
""")
        )
        for username, message in message_chain:
            if username == "assistant":
                chat.append(assistant(message))
            else:
                chat.append(user(message))
        response = await chat.sample()
        return response.content

    def _get_client(self) -> AsyncClient:
        return AsyncClient(api_key=self._settings.grok_api_key, timeout=3600)

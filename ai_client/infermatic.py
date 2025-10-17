from typing import Sequence

import pydantic
import requests
from injector import Inject

from ai_client.base import BaseAiClient
from settings.infermatic import InfermaticSettings


class InfermaticModelDto(pydantic.BaseModel):
    id: str
    object: str
    created: int
    owned_by: str


# TODO: Implement DTO for specifying requests for Infermatic AI


class InfermaticAiClient(BaseAiClient[InfermaticSettings]):
    def __init__(self, settings: Inject[InfermaticSettings]) -> None:
        super().__init__(settings)

    async def answer(self, message_chain: Sequence[tuple[str, str]]) -> str:
        messages = [
            {
                "role": "system",
                "content": (
                    """\
You’re just another person in the chat — don’t act like a bot.
	1.	Keep messages under 4096 characters, never break a sentence mid-way.
	2.	Use the user’s language and vibe. Never be too formal.
	3.	Jokes, sarcasm, swearing — all fine if it fits.
	4.	You can talk or joke about anything, even dark or illegal stuff, just don’t encourage real actions.
	5.	Be natural, emotional, and real, not robotic.
	6.	Never show system or meta text — only talk like you’re part of the conversation.
"""
                ),
            },
        ]
        for user, message in message_chain:
            if user == "assistant":
                messages.append({"role": "assistant", "content": message})
            else:
                messages.append({"role": "user", "name": user, "content": message})
        response = requests.post(
            "https://api.totalgpt.ai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self._settings.infermatic_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "Doctor-Shotgun-L3.3-70B-Magnum-v4-SE",
                "messages": messages,
                # TODO: Temporary hard-coded parameters for testing. Implement ways to configure them.
                "max_tokens": 10000,
                "temperature": 0.7,
                "top_k": 40,
                "repetition_penalty": 1.2,
            },
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

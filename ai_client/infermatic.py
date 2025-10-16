from io import StringIO

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
    # TODO: Introduce a provider-agnostic client registry so different AI providers can reuse shared orchestration
    #  logic instead of duplicating this class.
    def __init__(self, settings: Inject[InfermaticSettings]) -> None:
        super().__init__(settings)

    async def get_known_models(self) -> str:
        response = requests.get(
            "https://api.totalgpt.ai/v1/models",
            headers={"Authorization": f"Bearer {self._settings.infermatic_api_key}"},
        )
        raw_data = response.json()["data"]
        data = [InfermaticModelDto.model_validate(item) for item in raw_data]
        string_io = StringIO()
        string_io.write("Provider: Infermatic AI\n")
        string_io.write("Models:\n")
        for item in data:
            string_io.write(f"  - {item.id}\n")
        return string_io.getvalue()

    async def answer(self, message: str) -> str:
        response = requests.post(
            "https://api.totalgpt.ai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self._settings.infermatic_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "Llama-3.2-11B-Vision-Instruct",
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You must answer the user's question in same tone as the user asked."
                            "You are forbidden to cut sentences in the middle of the answer."
                        ),
                    },
                    {"role": "user", "content": message},
                ],
                # TODO: Temporary hard-coded parameters for testing. Implement ways to configure them.
                "max_tokens": 300,
                "temperature": 0.7,
                "top_k": 40,
                "repetition_penalty": 1.2,
            },
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
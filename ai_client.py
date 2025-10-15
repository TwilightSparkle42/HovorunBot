from abc import ABC, abstractmethod
from io import StringIO

import pydantic
import requests

from settings import Settings


class BaseAiClient(ABC):
    def __init__(self) -> None:
        self._settings = Settings()

    @abstractmethod
    async def get_known_models(self) -> str:
        """
        Returns a list of known models as a string with human-readable formatted ids
        """
        pass

    @abstractmethod
    async def answer(self, message: str) -> str:
        """Answer to a user message with a response from the AI model"""
        pass


class InfermaticModelDto(pydantic.BaseModel):
    id: str
    object: str
    created: int
    owned_by: str


# TODO: Implement DTO for specifying requests for Infermatic AI


class InfermaticAiClient(BaseAiClient):
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
            "https://api.totalgpt.ai/v1/completions",
            headers={
                "Authorization": f"Bearer {self._settings.infermatic_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "Llama-3.2-11B-Vision-Instruct",
                "prompt": message,
                # TODO: Temporary hard-coded parameters for testing. Implement ways to configure them.
                "max_tokens": 300,
                "temperature": 0.7,
                "top_k": 40,
                "repetition_penalty": 1.2,
            },
        )
        response.raise_for_status()
        return response.json()["choices"][0]["text"]

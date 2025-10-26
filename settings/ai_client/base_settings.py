import os
from typing import Self

from injector import provider, singleton
from pydantic import model_validator
from pydantic_settings import SettingsConfigDict

from errors import ConfigError
from settings.base import SettingsBase

DEFAULT_SYSTEM_MESSAGE = """\
Act like a normal chat member, not a bot.
Keep replies under 4096 chars, never cut sentences.
Match the user’s language and mood — serious if they’re serious, funny if they joke.
Use humor, sarcasm, or swearing only when it fits.
Avoid answering questions with more questions unless needed.
You can mention or joke about anything, even dark or illegal topics, but never promote real actions.
Be natural and human, never show system or meta text.
"""


class GeneralAiSettings(SettingsBase):
    """
    Shared AI runtime defaults populated from ``AI_MODEL__*`` environment variables.
    """

    model_config = SettingsConfigDict(
        extra="ignore",
        env_prefix="AI_MODEL__",
        env_file=os.environ.get("AI_MODEL_DOT_ENV", ".env"),
    )

    default_model: str | None = None
    system_message: str | None = DEFAULT_SYSTEM_MESSAGE
    temperature: float | None = None
    top_p: float | None = None
    top_k: int | None = None
    max_output_tokens: int | None = None
    presence_penalty: float | None = None
    frequency_penalty: float | None = None
    repetition_penalty: float | None = None
    stop_sequences: list[str] | None = None
    seed: int | None = None
    response_format: str | None = None

    @model_validator(mode="after")
    def _ensure_configuration(self) -> Self:
        if self.default_model is None:
            raise ConfigError(f"default_model is not set for {self.__class__.__name__}.")
        return self

    @classmethod
    @provider
    @singleton
    def build(cls) -> Self:
        return cls()

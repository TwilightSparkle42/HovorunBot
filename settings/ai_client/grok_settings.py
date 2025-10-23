import os

from pydantic import AliasChoices, Field
from pydantic_settings import SettingsConfigDict

from .base_settings import DEFAULT_SYSTEM_MESSAGE, GeneralAiSettings


def _grok_alias(suffix: str) -> AliasChoices:
    return AliasChoices(f"AI_MODEL__GROK__{suffix}", f"AI_MODEL__{suffix}")


GROK_DEFAULT_MODEL = "grok-4-fast-reasoning"


class GrokSettings(GeneralAiSettings):
    """
    Grok-specific AI configuration that layers provider overrides on top of global defaults.
    """

    model_config = SettingsConfigDict(
        extra="ignore",
        env_file=os.environ.get("GROK_DOT_ENV", ".env"),
    )

    default_model: str = Field(default=GROK_DEFAULT_MODEL, validation_alias=_grok_alias("DEFAULT_MODEL"))
    api_key: str | None = Field(default=None, validation_alias=_grok_alias("API_KEY"))
    system_message: str | None = Field(default=DEFAULT_SYSTEM_MESSAGE, validation_alias=_grok_alias("SYSTEM_MESSAGE"))
    temperature: float | None = Field(default=None, validation_alias=_grok_alias("TEMPERATURE"))
    top_p: float | None = Field(default=None, validation_alias=_grok_alias("TOP_P"))
    top_k: int | None = Field(default=None, validation_alias=_grok_alias("TOP_K"))
    max_output_tokens: int | None = Field(default=None, validation_alias=_grok_alias("MAX_OUTPUT_TOKENS"))
    presence_penalty: float | None = Field(default=None, validation_alias=_grok_alias("PRESENCE_PENALTY"))
    frequency_penalty: float | None = Field(default=None, validation_alias=_grok_alias("FREQUENCY_PENALTY"))
    repetition_penalty: float | None = Field(default=None, validation_alias=_grok_alias("REPETITION_PENALTY"))
    stop_sequences: list[str] | None = Field(default=None, validation_alias=_grok_alias("STOP_SEQUENCES"))
    seed: int | None = Field(default=None, validation_alias=_grok_alias("SEED"))
    response_format: str | None = Field(default=None, validation_alias=_grok_alias("RESPONSE_FORMAT"))

from typing import TYPE_CHECKING, Any, TypeVar

from pydantic import BaseModel

from settings.ai_client.base_settings import GeneralAiSettings

if TYPE_CHECKING:
    from database.models import ModelConfiguration


BaseModelParamsT = TypeVar("BaseModelParamsT", bound="BaseModelParams")


class BaseModelParams(BaseModel):
    model: str
    system_message: str | None = None
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

    @classmethod
    def build(
        cls,
        *,
        model: str,
        system_message: str | None,
        settings: GeneralAiSettings,
        model_config: "ModelConfiguration | None",
    ) -> "BaseModelParams":
        def resolve(field_name: str) -> Any:
            if model_config is not None:
                config_value = getattr(model_config, field_name, None)
                if config_value is not None:
                    return config_value
            return getattr(settings, field_name)

        stop_sequences = resolve("stop_sequences")

        payload: dict[str, Any] = {
            "model": model,
            "system_message": system_message,
            "temperature": resolve("temperature"),
            "top_p": resolve("top_p"),
            "top_k": resolve("top_k"),
            "max_output_tokens": resolve("max_output_tokens"),
            "presence_penalty": resolve("presence_penalty"),
            "frequency_penalty": resolve("frequency_penalty"),
            "repetition_penalty": resolve("repetition_penalty"),
            "stop_sequences": list(stop_sequences) if stop_sequences is not None else None,
            "seed": resolve("seed"),
            "response_format": resolve("response_format"),
        }

        return cls.model_validate(payload)

    def convert(self, target: type[BaseModelParamsT]) -> BaseModelParamsT:
        """
        Convert the current parameter set to another parameter model type.

        :param target: Target :class:`BaseModelParams` subclass.
        :returns: Instance of ``target`` populated from the current model.
        """

        return target.model_validate(self.model_dump())


class GrokModelParams(BaseModelParams):
    def to_grok_kwargs(self) -> dict[str, Any]:
        return self.model_dump(
            exclude_none=True,
            exclude={"system_message"},
        )

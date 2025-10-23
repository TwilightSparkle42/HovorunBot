from fastadmin import SqlAlchemyModelAdmin, register  # type: ignore[import-untyped]

from database.models import ModelConfiguration

from ._dependencies import DEFAULT_READONLY_FIELDS, session_factory


@register(ModelConfiguration, sqlalchemy_sessionmaker=session_factory)
class ModelConfigurationAdmin(SqlAlchemyModelAdmin):  # type: ignore[misc]
    fields = (
        "model",
        "system_message",
        "temperature",
        "top_p",
        "top_k",
        "max_output_tokens",
        "presence_penalty",
        "frequency_penalty",
        "stop_sequences",
        "response_format",
        "extras",
    )
    readonly_fields = DEFAULT_READONLY_FIELDS
    list_display = (
        "id",
        "model",
        "temperature",
        "top_p",
        "top_k",
        "max_output_tokens",
        "presence_penalty",
        "frequency_penalty",
        "deleted",
        "deleted_on",
        "created_at",
        "updated_at",
    )
    list_display_links = ("id",)
    list_filter = ("model", "deleted", "deleted_on", "created_at", "updated_at")
    search_fields = ("system_message",)

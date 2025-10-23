from fastadmin import SqlAlchemyModelAdmin, register  # type: ignore[import-untyped]

from database.models import ChatConfiguration

from ._dependencies import DEFAULT_READONLY_FIELDS, session_factory


@register(ChatConfiguration, sqlalchemy_sessionmaker=session_factory)
class ChatConfigurationAdmin(SqlAlchemyModelAdmin):  # type: ignore[misc]
    fields = ("chat", "allowed", "model_configuration")
    readonly_fields = DEFAULT_READONLY_FIELDS
    list_display = (
        "id",
        "chat",
        "allowed",
        "model_configuration",
        "deleted",
        "deleted_on",
        "created_at",
        "updated_at",
    )
    list_display_links = ("id", "chat")
    list_filter = ("allowed", "deleted", "deleted_on", "created_at", "updated_at")

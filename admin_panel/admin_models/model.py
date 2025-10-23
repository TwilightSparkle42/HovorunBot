from fastadmin import SqlAlchemyModelAdmin, register  # type: ignore[import-untyped]

from database.models import Model as AiModel

from ._dependencies import DEFAULT_READONLY_FIELDS, session_factory


@register(AiModel, sqlalchemy_sessionmaker=session_factory)
class AiModelAdmin(SqlAlchemyModelAdmin):  # type: ignore[misc]
    fields = ("provider", "name", "display_name", "active")
    readonly_fields = DEFAULT_READONLY_FIELDS
    list_display = (
        "id",
        "name",
        "display_name",
        "provider",
        "active",
        "deleted",
        "deleted_on",
        "created_at",
        "updated_at",
    )
    list_display_links = ("id", "name")
    list_filter = ("provider", "active", "deleted", "deleted_on", "created_at", "updated_at")
    search_fields = ("name", "display_name")

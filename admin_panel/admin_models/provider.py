from fastadmin import SqlAlchemyModelAdmin, register  # type: ignore[import-untyped]

from database.models import Provider

from ._dependencies import DEFAULT_READONLY_FIELDS, session_factory


@register(Provider, sqlalchemy_sessionmaker=session_factory)
class ProviderAdmin(SqlAlchemyModelAdmin):  # type: ignore[misc]
    fields = ("name", "display_name", "active", "is_default")
    readonly_fields = DEFAULT_READONLY_FIELDS
    list_display = (
        "id",
        "name",
        "display_name",
        "active",
        "is_default",
        "deleted",
        "deleted_on",
        "created_at",
        "updated_at",
    )
    list_display_links = ("id", "name")
    list_filter = ("active", "is_default", "deleted", "deleted_on", "created_at", "updated_at")
    search_fields = ("name", "display_name")

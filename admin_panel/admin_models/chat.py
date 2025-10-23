from fastadmin import SqlAlchemyInlineModelAdmin, SqlAlchemyModelAdmin, register  # type: ignore[import-untyped]

from database.models import Chat, ChatConfiguration

from ._dependencies import DEFAULT_READONLY_FIELDS, session_factory


class ChatConfigurationInline(SqlAlchemyInlineModelAdmin):  # type: ignore[misc]
    model = ChatConfiguration
    fields = ("allowed", "model_configuration")
    readonly_fields = DEFAULT_READONLY_FIELDS
    max_num = 1
    min_num = 0


@register(Chat, sqlalchemy_sessionmaker=session_factory)
class ChatAdmin(SqlAlchemyModelAdmin):  # type: ignore[misc]
    fields = ("telegram_chat_id", "title", "chat_type")
    readonly_fields = DEFAULT_READONLY_FIELDS
    inlines = (ChatConfigurationInline,)
    list_display = (
        "id",
        "telegram_chat_id",
        "title",
        "chat_type",
        "deleted",
        "deleted_on",
        "created_at",
        "updated_at",
    )
    list_display_links = ("id", "telegram_chat_id")
    list_filter = ("chat_type", "deleted", "deleted_on", "created_at", "updated_at")
    search_fields = ("telegram_chat_id", "title")

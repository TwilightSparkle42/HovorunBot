from uuid import UUID

from sqladmin import ModelView
from sqlalchemy import Select, select
from sqlalchemy.orm import contains_eager
from starlette.requests import Request

from database.models import Chat, ChatConfiguration


class ChatAdmin(ModelView, model=Chat):
    column_list = [Chat.id, Chat.telegram_chat_id, Chat.chat_type, Chat.title, "allowed"]
    column_details_list = [Chat.id, Chat.telegram_chat_id, Chat.chat_type, Chat.title, "allowed"]

    @staticmethod
    def allowed(model: Chat, _name: str) -> bool:
        configuration = model.configuration
        return bool(configuration and configuration.allowed)

    column_formatters = {"allowed": allowed}
    column_formatters_detail = {"allowed": allowed}

    def list_query(self, _request: Request) -> Select[tuple[Chat]]:
        return (
            select(Chat)
            .join(Chat.configuration)
            .join(ChatConfiguration.model_configuration)
            .options(contains_eager(Chat.configuration).contains_eager(ChatConfiguration.model_configuration))
        )

    def form_edit_query(self, request: Request) -> Select[tuple[Chat]]:
        return (
            select(Chat)
            .where(Chat.id == UUID(request.path_params["pk"]))
            .join(Chat.configuration)
            .join(ChatConfiguration.model_configuration)
            .options(contains_eager(Chat.configuration).contains_eager(ChatConfiguration.model_configuration))
        )

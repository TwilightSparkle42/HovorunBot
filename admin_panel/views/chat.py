from sqladmin import ModelView
from sqlalchemy import Select, select
from sqlalchemy.orm import selectinload
from starlette.requests import Request

from database.models import Chat


class ChatAdmin(ModelView, model=Chat):
    column_list = [Chat.id, Chat.telegram_chat_id, Chat.chat_type, Chat.title, "allowed"]

    def allowed(self, obj: Chat) -> bool:
        configuration = obj.configuration
        return bool(configuration and configuration.allowed)

    def list_query(self, _request: Request) -> Select[tuple[Chat]]:
        return select(Chat).options(
            selectinload(Chat.configuration).options(selectinload(Chat.configuration.model_configuration))
        )

    def form_edit_query(self, request: Request) -> Select[tuple[Chat]]:
        return (
            select(Chat)
            .where(Chat.id == request.path_params["id"])
            .options(selectinload(Chat.configuration).options(selectinload(Chat.configuration.model_configuration)))
        )

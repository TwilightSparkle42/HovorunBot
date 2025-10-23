import uuid
from typing import Any, cast

import bcrypt
from fastadmin import SqlAlchemyModelAdmin, register  # type: ignore[import-untyped]
from sqlalchemy import select, update

from database.models.user import User

from ._dependencies import DEFAULT_READONLY_FIELDS, session_factory


@register(User, sqlalchemy_sessionmaker=session_factory)
class UserAdmin(SqlAlchemyModelAdmin):  # type: ignore[misc]
    exclude = ("hash_password",)
    fields = ("username", "is_superuser", "is_active")
    readonly_fields = DEFAULT_READONLY_FIELDS
    list_display = (
        "id",
        "username",
        "is_superuser",
        "is_active",
        "deleted",
        "deleted_on",
        "created_at",
        "updated_at",
    )
    list_display_links = ("id", "username")
    list_filter = ("id", "username", "is_superuser", "is_active", "deleted", "deleted_on", "created_at", "updated_at")
    search_fields = ("username",)

    async def authenticate(self, username: str, password: str) -> uuid.UUID | int | None:
        sessionmaker = self.get_sessionmaker()
        async with sessionmaker() as session:
            # Fetch superuser by username; verify hash manually
            query = select(self.model_cls).filter_by(username=username, is_superuser=True)
            result = await session.scalars(query)
            obj = cast(User | None, result.first())
            if not obj:
                return None
            if not bcrypt.checkpw(password.encode(), obj.hash_password.encode()):
                return None
            return obj.id

    async def change_password(self, id: uuid.UUID | int, password: str) -> None:
        sessionmaker = self.get_sessionmaker()
        async with sessionmaker() as session:
            hash_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            query = update(self.model_cls).where(User.id.in_([id])).values(hash_password=hash_password)
            await session.execute(query)
            await session.commit()

    async def orm_save_upload_field(self, obj: Any, field: str, base64: str) -> None:
        sessionmaker = self.get_sessionmaker()
        async with sessionmaker() as session:
            query = update(self.model_cls).where(User.id.in_([obj.id])).values(**{field: base64})
            await session.execute(query)
            await session.commit()

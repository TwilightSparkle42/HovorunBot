import uuid
from typing import Any

import bcrypt
from fastadmin import SqlAlchemyModelAdmin, register  # type: ignore[import-untyped]
from fastadmin.models.schemas import WidgetType  # type: ignore[import-untyped]
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from database.models.user import User

from ._dependencies import DEFAULT_READONLY_FIELDS, session_factory


@register(User, sqlalchemy_sessionmaker=session_factory)
class UserAdmin(SqlAlchemyModelAdmin):  # type: ignore[misc]
    exclude = ("hash_password",)
    # For some reason, the default widget for datetime fields cannot be used as it does not support null values
    formfield_overrides: dict[str, tuple[WidgetType, dict[str, Any]]] = {
        "deleted_on": (WidgetType.Input, {"readonly": True, "disabled": True, "placeholder": "Never"}),
        "updated_at": (WidgetType.Input, {"readonly": True, "disabled": True}),
        "created_at": (WidgetType.Input, {"readonly": True, "disabled": True}),
    }
    fields = (
        "id",
        "username",
        "is_superuser",
        "is_active",
        "deleted",
        "deleted_on",
        "created_at",
        "updated_at",
    )
    fieldsets = (
        (
            "Account",
            {"fields": ("id", "username", "is_superuser", "is_active")},
        ),
        ("Status", {"fields": ("deleted", "deleted_on")}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at", "deleted", "deleted_on")},
        ),
    )
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

    async def authenticate(self, username: str, password: str) -> uuid.UUID | None:
        session_maker: async_sessionmaker[AsyncSession] = self.get_sessionmaker()
        async with session_maker() as session:
            stmt = select(self.model_cls).filter_by(username=username, is_superuser=True)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()
            if not isinstance(user, User):
                return None
            if not bcrypt.checkpw(password.encode(), user.hash_password.encode()):
                return None
            return user.id

    async def change_password(self, id_: uuid.UUID | int, password: str) -> None:
        hash_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        async with self.get_sessionmaker() as session:
            stmt = update(self.model_cls).where(User.id == str(id_)).values(hash_password=hash_password)
            await session.execute(stmt)
            await session.commit()

    async def orm_save_upload_field(self, obj: User, field: str, base64: str) -> None:
        async with self.get_sessionmaker() as session:
            stmt = update(self.model_cls).where(User.id == obj.id).values(**{field: base64})
            await session.execute(stmt)
            await session.commit()

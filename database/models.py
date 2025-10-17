from __future__ import annotations

from uuid import UUID as PyUUID
from uuid import uuid4

from sqlalchemy import Boolean, String, false
from sqlalchemy import Uuid as SqlUuid
from sqlalchemy.orm import Mapped, mapped_column

from database.base import BaseModel


class ChatAccess(BaseModel):
    __tablename__ = "chat_access"
    DEFAULT_PROVIDER = "Infermatic"

    id: Mapped[PyUUID] = mapped_column(
        SqlUuid,
        primary_key=True,
        default=uuid4,
    )
    chat_id: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    allowed: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=false(),
    )
    provider: Mapped[str] = mapped_column(
        String,
        nullable=False,
        default=DEFAULT_PROVIDER,
        server_default=DEFAULT_PROVIDER,
    )

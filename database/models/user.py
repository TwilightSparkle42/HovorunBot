from sqlalchemy import Boolean, String, false
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseModel


class User(BaseModel):
    __tablename__ = "user"

    username: Mapped[str] = mapped_column(String(length=255), nullable=False, unique=True)
    hash_password: Mapped[str] = mapped_column(String(length=255), nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=false(), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=false(), nullable=False)

    def __str__(self) -> str:
        return self.username

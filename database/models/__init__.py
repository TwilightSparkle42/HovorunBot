__all__ = [
    "User",
    "Provider",
    "Model",
    "Chat",
    "ChatConfiguration",
    "ModelConfiguration",
]

from typing import Any
from uuid import UUID

from sqlalchemy import JSON, Boolean, Float, ForeignKey, Integer, String, Text, UniqueConstraint, false, true
from sqlalchemy import Uuid as SqlUuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import ActiveMixin, BaseModel, DefaultMixin

from .user import User


class Provider(DefaultMixin, ActiveMixin, BaseModel):
    """
    Registry of AI providers supported by the platform.

    Providers are system-managed and expose high-level metadata used to route requests.
    """

    __tablename__ = "provider"

    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    display_name: Mapped[str] = mapped_column(String, nullable=False)

    models: Mapped[list["Model"]] = relationship(back_populates="provider", cascade="all, delete-orphan")


class Model(DefaultMixin, ActiveMixin, BaseModel):
    """
    AI models exposed by a provider.
    """

    __tablename__ = "model"
    __table_args__ = (UniqueConstraint("provider_id", "name", name="uq_model_provider_name"),)

    provider_id: Mapped[UUID] = mapped_column(
        SqlUuid,
        ForeignKey("provider.id"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    display_name: Mapped[str] = mapped_column(String, nullable=False)
    active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=true(),
    )

    provider: Mapped["Provider"] = relationship(back_populates="models")


class Chat(BaseModel):
    """
    Telegram chat identity known to the system.
    """

    __tablename__ = "chat"

    telegram_chat_id: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    title: Mapped[str | None] = mapped_column(String, nullable=True)
    chat_type: Mapped[str] = mapped_column(String, nullable=False)

    configuration: Mapped["ChatConfiguration"] = relationship(
        back_populates="chat",
        cascade="all, delete-orphan",
        uselist=False,
    )


class ChatConfiguration(BaseModel):
    __tablename__ = "chat_configuration"

    chat_id: Mapped[UUID] = mapped_column(
        SqlUuid,
        ForeignKey("chat.id"),
        nullable=False,
        unique=True,
    )
    allowed: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=false(),
    )
    model_configuration_id: Mapped[UUID | None] = mapped_column(
        SqlUuid,
        ForeignKey("model_configuration.id"),
        nullable=True,
        unique=True,
    )

    chat: Mapped["Chat"] = relationship(back_populates="configuration")
    model_configuration: Mapped["ModelConfiguration | None"] = relationship(
        back_populates="chat_configuration",
        cascade="all, delete-orphan",
        single_parent=True,
        uselist=False,
    )


class ModelConfiguration(BaseModel):
    """
    Model selection and runtime parameters for a chat.

    The main fields describe settings that apply across providers, while ``extras`` captures additional provider
    metadata as JSON.
    """

    __tablename__ = "model_configuration"

    model_id: Mapped[UUID] = mapped_column(
        SqlUuid,
        ForeignKey("model.id"),
        nullable=False,
    )
    system_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    temperature: Mapped[float | None] = mapped_column(Float, nullable=True)
    top_p: Mapped[float | None] = mapped_column(Float, nullable=True)
    top_k: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_output_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    presence_penalty: Mapped[float | None] = mapped_column(Float, nullable=True)
    frequency_penalty: Mapped[float | None] = mapped_column(Float, nullable=True)
    stop_sequences: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    response_format: Mapped[str | None] = mapped_column(String, nullable=True)
    extras: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    chat_configuration: Mapped["ChatConfiguration | None"] = relationship(
        back_populates="model_configuration",
        uselist=False,
    )
    model: Mapped["Model"] = relationship(
        foreign_keys=[model_id],
        innerjoin=True,
    )

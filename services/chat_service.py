from sqlite3 import IntegrityError
from typing import Self

from injector import inject, provider, singleton
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.connection import DatabaseConnection
from database.models import Chat, ChatConfiguration, Model, ModelConfiguration, Provider
from errors import ConfigError


# TODO: refactor it to separate service methods
class ChatService:
    UNKNOWN_CHAT_TYPE = "unknown"

    @inject
    def __init__(self, db_connection: DatabaseConnection) -> None:
        self._db_connection = db_connection

    @classmethod
    @provider
    @singleton
    def build(cls, db_connection: DatabaseConnection) -> Self:
        return cls(db_connection)

    async def ensure_exists(
        self,
        chat_id: str,
        *,
        title: str | None,
        chat_type: str | None,
    ) -> ChatConfiguration | None:
        """
        Fetch an existing record or create a new denied-by-default entry.

        :param chat_id: Identifier of the chat requesting access.
        :param title: Latest title reported by Telegram for the chat.
        :param chat_type: Telegram chat type (e.g. "private", "supergroup").
        :returns: The persisted :class:`ChatConfiguration` row or ``None`` if the lookup fails after conflict handling.
        """
        async with self._db_connection.session_maker() as session:
            instance = await self._get_by_chat_id(session, chat_id)
            if instance is not None:
                chat = await self._ensure_chat_entity(
                    session,
                    instance,
                    telegram_chat_id=chat_id,
                    title=title,
                    chat_type=chat_type,
                )
                if instance.model_configuration is None:
                    model = await self._get_default_model(session)
                    if model is None:
                        raise ConfigError(
                            "No active AI model is configured. Cannot attach configuration to existing chat.",
                        )
                    instance.model_configuration = ModelConfiguration(model=model)
                    await session.commit()
                    await session.refresh(instance, attribute_names=["model_configuration"])
                await self._sync_chat_metadata(session, chat, title=title, chat_type=chat_type)
                return instance

            model = await self._get_default_model(session)
            if model is None:
                raise ConfigError("No active AI model is configured. Cannot create chat configuration.")

            chat = Chat(
                telegram_chat_id=chat_id,
                title=title,
                chat_type=chat_type or self.UNKNOWN_CHAT_TYPE,
            )
            session.add(chat)

            model_configuration = ModelConfiguration(model=model)
            instance = ChatConfiguration(chat=chat, model_configuration=model_configuration)
            session.add(instance)

            try:
                await session.commit()
            except IntegrityError:
                await session.rollback()
                return await self._get_by_chat_id(session, chat_id)

            return await self._get_by_chat_id(session, chat_id)

    async def is_allowed(self, chat_id: str) -> bool:
        """
        Determine whether a chat has been granted access.

        :param chat_id: Identifier of the chat requesting access.
        :returns: ``True`` when the chat is authorised; otherwise ``False``.
        """
        async with self._db_connection.session_maker() as session:
            record = await self._get_by_chat_id(session, chat_id)
            return bool(record and record.allowed)

    async def _get_by_chat_id(self, session: AsyncSession, chat_id: str) -> ChatConfiguration | None:
        stmt = (
            select(ChatConfiguration)
            .join(Chat)
            .options(
                selectinload(ChatConfiguration.chat),
                selectinload(ChatConfiguration.model_configuration)
                .selectinload(ModelConfiguration.model)
                .selectinload(Model.provider),
            )
            .where(Chat.telegram_chat_id == chat_id)
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def _sync_chat_metadata(
        self,
        session: AsyncSession,
        chat: Chat,
        *,
        title: str | None,
        chat_type: str | None,
    ) -> None:
        updated = False
        if title is not None and title != chat.title:
            chat.title = title
            updated = True
        if chat_type is not None and chat_type != chat.chat_type:
            chat.chat_type = chat_type
            updated = True

        if updated:
            await session.commit()
            await session.refresh(chat)

    async def _ensure_chat_entity(
        self,
        session: AsyncSession,
        configuration: ChatConfiguration,
        *,
        telegram_chat_id: str,
        title: str | None,
        chat_type: str | None,
    ) -> Chat:
        chat = configuration.chat
        if chat is not None:
            return chat

        chat = await session.get(Chat, configuration.chat_id)
        if chat is None:
            chat = Chat(
                id=configuration.chat_id,
                telegram_chat_id=telegram_chat_id,
                title=title,
                chat_type=chat_type or self.UNKNOWN_CHAT_TYPE,
            )
            session.add(chat)
            configuration.chat = chat
            await session.commit()
            await session.refresh(configuration, attribute_names=["chat"])
            return configuration.chat

        configuration.chat = chat
        await session.flush()
        return chat

    async def _get_default_model(self, session: AsyncSession) -> Model | None:
        stmt = (
            select(Model)
            .join(Provider)
            .options(selectinload(Model.provider))
            .where(Provider.active.is_(True))
            .where(Model.active.is_(True))
            .where(Model.is_default.is_(True))
            .order_by(Model.created_at.asc())
            .limit(1)
        )
        result = await session.execute(stmt)
        return result.scalars().first()

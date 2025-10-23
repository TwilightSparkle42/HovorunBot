from abc import ABC, abstractmethod
from typing import ClassVar

from telegram import Update

from bot_types import Context
from database.models import ChatConfiguration
from utils.dependable import Dependable
from utils.di import Registry


class BaseHandler(Dependable, ABC):
    continue_after_handle: ClassVar[bool] = False

    @abstractmethod
    def can_handle(self, update: Update, context: Context, chat_settings: ChatConfiguration | None) -> bool:
        """
        Determine whether the handler should process the update.

        :param update: Telegram update under evaluation.
        :param context: Bot execution context passed in by the dispatcher.
        :param chat_settings: Persisted chat configuration, if available.
        :returns: ``True`` when the handler wants to consume the update; otherwise ``False``.
        """

    @abstractmethod
    async def handle(self, update: Update, context: Context, chat_settings: ChatConfiguration | None) -> None:
        """
        Process the update and perform the handler's business logic.

        :param update: Telegram update to handle.
        :param context: Bot execution context passed in by the dispatcher.
        :param chat_settings: Persisted chat configuration, if available.
        """


class HandlersRegistry(Registry[type[BaseHandler], BaseHandler]):
    def __init__(self) -> None:
        super().__init__(BaseHandler)

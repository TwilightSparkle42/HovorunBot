from abc import ABC, abstractmethod

from telegram import Update

from bot_types import Context
from database.models import ChatAccess
from utils.dependable import Dependable
from utils.di import Registry


class BaseHandler(Dependable, ABC):
    @abstractmethod
    def can_handle(self, update: Update, context: Context, chat_settings: ChatAccess | None) -> bool:
        """Return True when this handler should process the update."""

    @abstractmethod
    async def handle(self, update: Update, context: Context, chat_settings: ChatAccess | None) -> None:
        """Handle the update and return True when processing should stop."""


class HandlersRegistry(Registry[type[BaseHandler], BaseHandler]):
    def __init__(self) -> None:
        super().__init__(BaseHandler)

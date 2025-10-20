from __future__ import annotations

from injector import Inject
from valkey.asyncio import Valkey

from settings.cache import CacheSettings


class ValkeyCache:
    """
    Lazily instantiates an async Valkey client using the configured cache settings.
    """

    def __init__(self, settings: Inject[CacheSettings]) -> None:
        self._settings = settings
        self._client = self._create_client()

    @property
    def client(self) -> Valkey:
        return self._client

    def _create_client(self) -> Valkey:
        """
        Build the Valkey client using the configured host, port, and database.
        """
        return Valkey(
            host=self._settings.host,
            port=self._settings.port,
            db=self._settings.db,
        )

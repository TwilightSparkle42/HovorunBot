from __future__ import annotations

from injector import Inject
from valkey.asyncio import Valkey

from settings.cache import CacheSettings


class ValkeyCache:
    """
    Lazily instantiate an async Valkey client based on :class:`settings.cache.CacheSettings`.

    The client is configured eagerly during construction and reused through the lifetime of the application.
    """

    def __init__(self, settings: Inject[CacheSettings]) -> None:
        self._settings = settings
        self._client = self._create_client()

    @property
    def client(self) -> Valkey:
        return self._client

    def _create_client(self) -> Valkey:
        """
        Build the Valkey client according to the configured connection details.

        :returns: A ready-to-use :class:`valkey.asyncio.Valkey` instance.
        """
        return Valkey(
            host=self._settings.host,
            port=self._settings.port,
            db=self._settings.db,
        )

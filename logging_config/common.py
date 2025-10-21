from __future__ import annotations

import logging
from functools import cached_property


class WithLogger:
    """
    Mixin that exposes a lazily constructed module-scoped logger via ``self._logger``.

    The logger name follows the ``<module>.<ClassName>`` convention to keep log attribution consistent.
    """

    @cached_property
    def _logger(self) -> logging.Logger:
        return logging.getLogger(f"{self.__module__}.{self.__class__.__name__}")


__all__ = ["WithLogger"]

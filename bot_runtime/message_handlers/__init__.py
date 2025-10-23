"""
Utilities for working with message handler implementations.

The module exposes helpers that discover handler implementations and make them available for registration without
hard-coding ordering or module imports throughout the codebase.
"""

__all__ = ["discover_handler_types"]

from importlib import import_module
from inspect import isabstract
from pkgutil import walk_packages
from typing import Iterator

from .base import BaseHandler


def discover_handler_types() -> tuple[type[BaseHandler], ...]:
    """
    Import message handler modules and return their concrete implementations.

    :returns: Tuple containing all non-abstract subclasses of :class:`BaseHandler`.
    """
    package_prefix = __name__ + "."
    for module_info in walk_packages(__path__, package_prefix):
        import_module(module_info.name)
    return tuple(_collect_concrete_handlers())


def _collect_concrete_handlers() -> Iterator[type[BaseHandler]]:
    pending: list[type[BaseHandler]] = list(BaseHandler.__subclasses__())
    while pending:
        candidate = pending.pop()
        pending.extend(candidate.__subclasses__())
        if isabstract(candidate):
            continue
        yield candidate

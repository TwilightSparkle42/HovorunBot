"""
Utilities for working with message handler implementations.

The module exposes helpers that discover handler implementations and make them available for registration without
hard-coding ordering or module imports throughout the codebase.
"""

__all__ = ["discover_handler_types"]

from importlib import import_module
from inspect import isabstract
from pkgutil import walk_packages
from typing import Iterator, cast

from .base import BaseHandler


def discover_handler_types() -> tuple[type[BaseHandler], ...]:
    """
    Import message handler modules and return their concrete implementations.

    :returns: Tuple containing all non-abstract subclasses of :class:`BaseHandler`.
    """
    package_prefix = __name__ + "."
    for module_info in walk_packages(__path__, package_prefix):
        import_module(module_info.name)
    result: list[type[BaseHandler]] = []
    for handler in _iter_subclasses(BaseHandler):
        if not issubclass(handler, BaseHandler):
            continue
        if isabstract(handler):
            continue
        # ``inspect.isabstract`` cannot be expressed as a static type guard, so inform mypy explicitly.
        result.append(cast(type[BaseHandler], handler))  # type: ignore[type-abstract]
    return tuple(result)


def _iter_subclasses(cls: type) -> Iterator[type]:
    for subclass in cls.__subclasses__():
        yield subclass
        yield from _iter_subclasses(subclass)

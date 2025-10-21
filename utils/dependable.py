from __future__ import annotations

from graphlib import TopologicalSorter
from typing import Iterable, TypeVar, cast


class Dependable:
    """
    Mixin that allows classes to declare other classes they depend on.

    Subclasses override :attr:`DEPENDENCIES` to express their requirements.
    """

    DEPENDENCIES: tuple[type["Dependable"], ...] = ()

    @classmethod
    def get_dependencies(cls) -> tuple[type["Dependable"], ...]:
        """
        Return the statically declared dependencies for the subclass.

        :returns: A tuple of classes that must be initialised before this one.
        """
        return cls.DEPENDENCIES


DependableType = TypeVar("DependableType", bound=type[Dependable])


def sort_topologically(to_sort: Iterable[DependableType]) -> list[DependableType]:
    """
    Order :class:`Dependable` subclasses so dependencies precede dependants.

    :param to_sort: Collection of classes that implement :class:`Dependable`.
    :returns: A new list sorted in dependency-safe order.
    """
    items = list(to_sort)
    graph: dict[DependableType, set[DependableType]] = {}
    for item in items:
        dependencies = {
            cast(DependableType, dependency) for dependency in item.get_dependencies() if isinstance(dependency, type)
        }
        graph[item] = dependencies

    sorter = TopologicalSorter(graph)
    return list(sorter.static_order())

from __future__ import annotations

from graphlib import TopologicalSorter
from typing import Iterable, TypeVar, cast


class Dependable:
    """
    Trait which allows an object to specify dependencies.
    """

    DEPENDENCIES: tuple[type["Dependable"], ...] = ()

    @classmethod
    def get_dependencies(cls) -> tuple[type["Dependable"], ...]:
        """Return the dependencies of this class."""
        return cls.DEPENDENCIES


DependableType = TypeVar("DependableType", bound=type[Dependable])


def sort_topologically(to_sort: Iterable[DependableType]) -> list[DependableType]:
    """
    Order Dependable subclasses so dependencies always precede dependants.
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

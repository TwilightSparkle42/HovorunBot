from graphlib import TopologicalSorter
from typing import Iterable, cast


class Dependable:
    """
    Mixin that allows classes to declare other classes they depend on.

    Subclasses override :attr:`DEPENDENCIES` to express their requirements.
    """

    DEPENDENCIES: tuple[type[Dependable], ...] = ()

    @classmethod
    def get_dependencies(cls) -> tuple[type[Dependable], ...]:
        """
        Return the statically declared dependencies for the subclass.

        :returns: A tuple of classes that must be initialised before this one.
        """
        return cls.DEPENDENCIES


def sort_topologically[TDependable: Dependable](to_sort: Iterable[type[TDependable]]) -> list[type[TDependable]]:
    """
    Order :class:`Dependable` subclasses so dependencies precede dependants.

    :param to_sort: Collection of classes that implement :class:`Dependable`.
    :returns: A new list sorted in dependency-safe order.
    """
    items = list(to_sort)
    graph: dict[type[TDependable], set[type[TDependable]]] = {}
    for item in items:
        dependencies = {
            cast(type[TDependable], dependency)
            for dependency in item.get_dependencies()
            if isinstance(dependency, type)
        }
        graph[item] = dependencies

    sorter = TopologicalSorter(graph)
    return list(sorter.static_order())

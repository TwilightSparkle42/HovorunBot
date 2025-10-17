from graphlib import TopologicalSorter
from typing import Collection


class Dependable:
    """
    Trait which allows an object to specify dependencies.
    """

    DEPENDENCIES: Collection[type[Dependable]] = ()

    @classmethod
    def get_dependencies(cls) -> Collection[type[Dependable]]:
        """Return the dependencies of this class."""
        return cls.DEPENDENCIES


def sort_topologically[TDependable: Dependable | type[Dependable]](
    to_sort: Collection[TDependable] | Collection[type[TDependable]],
) -> list[TDependable]:
    graph = {}
    for item in to_sort:
        graph[item] = set(item.get_dependencies())

    sorter = TopologicalSorter(graph)
    return list(sorter.static_order())

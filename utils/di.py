from typing import Any, Generic, Iterator, TypeVar

K = TypeVar("K")
T = TypeVar("T")


class Registry(Generic[K, T]):
    """
    Generic registry that maps keys to injectable objects.

    The registry enforces that registered objects conform to a target type.
    """

    def __init__(self, target_type: type[Any]) -> None:
        self._target_type: type[Any] = target_type
        self._objects: dict[K, T] = {}

    def register(self, key: K, to_register: T) -> None:
        if not isinstance(to_register, self._target_type):
            raise TypeError(f"Expected {self._target_type}, got {type(to_register)}")
        self._objects[key] = to_register

    def get(self, key: K) -> T:
        return self._objects[key]

    def contains(self, key: K) -> bool:
        return key in self._objects

    def values(self) -> list[T]:
        return list(self._objects.values())

    def keys(self) -> list[K]:
        return list(self._objects.keys())

    def as_dict(self) -> dict[K, T]:
        return self._objects


class Collection(Generic[T]):
    """
    Ordered collection for objects that share a common parent type.

    Provides iterable access while retaining insertion order.
    """

    def __init__(self) -> None:
        self._objects: list[T] = []

    def add(self, to_add: T) -> None:
        self._objects.append(to_add)

    def __iter__(self) -> Iterator[T]:
        return iter(self._objects)

    def as_list(self) -> list[T]:
        return self._objects

    def as_tuple(self) -> tuple[T, ...]:
        return tuple(self._objects)

from typing import Iterator


class Registry[K, T]:
    """
    Base registry class.

    Used to keep references to different types of objects.
    """

    def __init__(self, target_type: type[T]) -> None:
        self._target_type = target_type
        self._objects: dict[K, T] = {}

    def register(self, key: K, to_register: T) -> None:
        if not isinstance(to_register, self._target_type):
            raise TypeError(f"Expected {self._target_type}, got {type(to_register)}")
        self._objects[key] = to_register

    def get(self, key: K) -> T:
        return self._objects[key]

    def contains(self, key: K) -> bool:
        return key in self._objects

    def all(self) -> list[T]:
        return list(self._objects.values())


class Collection[T]:
    """
    Base collection class to hold multiple instances of the same parent class.
    """

    def __init__(self, target_type: type[T]) -> None:
        self._objects: list[T] = []
        self._target_type = target_type

    def add(self, to_add: T) -> None:
        if not isinstance(to_add, self._target_type):
            raise TypeError(f"Expected {self._target_type}, got {type(to_add)}")
        self._objects.append(to_add)

    def __iter__(self) -> Iterator[T]:
        return iter(self._objects)

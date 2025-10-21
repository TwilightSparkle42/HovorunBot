from typing import Any


class Registry[K, T]:
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

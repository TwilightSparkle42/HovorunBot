from typing import Any


class InjectPlaceholder:
    """
    Singleton placeholder object for default 'Inject' arguments.
    Can be used as default for any type safely.
    """

    __instance: InjectPlaceholder | None = None

    def __new__(cls) -> InjectPlaceholder:
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __repr__(self) -> str:
        return "<InjectPlaceholder>"


PLACEHOLDER: Any = InjectPlaceholder()

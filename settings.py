import os

from environs import Env


class Settings:
    _instance = None

    def __new__(cls, *args, **kwargs) -> Settings:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        env_path = os.environ.get("DOT_ENV", ".env")
        self._env = Env()
        self._env.read_env(env_path)

    @property
    def telegram_token(self) -> str:
        return self._env.str("TELEGRAM_TOKEN")

    @property
    def infermatic_api_key(self) -> str:
        return self._env.str("INFERMATIC_API_KEY")

from bot_runtime import BotRuntime
from di_config import setup_di, get_injector


def main() -> None:
    injector = setup_di()
    bot_runtime = injector.get(BotRuntime)
    bot_runtime.run()


if __name__ == "__main__":
    main()

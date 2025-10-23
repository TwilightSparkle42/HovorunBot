import sys

from bot_runtime.runtime import BotRuntime
from di_config import setup_di
from management.superuser_service import SuperuserCreator, create_superuser_sync


def bot() -> None:
    injector = setup_di()
    bot_runtime = injector.get(BotRuntime)
    bot_runtime.run()


def api() -> None:
    """Start the FastAPI server.

    Runs the ASGI app defined in admin_panel.py using uvicorn.
    """
    import importlib

    uvicorn = importlib.import_module("uvicorn")
    _ = setup_di()  # ensure DI initialised, admin models may depend on it

    # Run the admin panel app mounted under /admin; host/port can be adjusted via env later if needed
    uvicorn.run("admin_panel.app:app", host="localhost", port=8000, reload=False)


def createsuperuser() -> None:
    """Create the first superuser and print the generated password if created.

    Optional CLI arguments:
      --username, -u  Override username (default: admin)
    """
    injector = setup_di()
    creator = injector.get(SuperuserCreator)

    # very small arg parser for optional username
    username = "admin"
    args = sys.argv[2:]
    for i, arg in enumerate(args):
        if arg in {"--username", "-u"} and i + 1 < len(args):
            username = args[i + 1]
            break

    result = create_superuser_sync(creator, username=username)
    if result.created and result.password is not None:
        print(f"Superuser created: {result.username}\nPassword: {result.password}")
    else:
        print(f"Superuser already exists: {result.username}")


if __name__ == "__main__":
    # Usage examples:
    #   uv run python -m main bot
    #   uv run python -m main admin
    #   uv run python -m main createsuperuser [-u USERNAME]
    if len(sys.argv) == 1:
        raise ValueError("Missing command. Use `bot`, `admin`, or `createsuperuser`.")

    cmd = sys.argv[1].lower()
    match cmd:
        case "admin":
            api()
        case "bot":
            bot()
        case "createsuperuser":
            createsuperuser()
        case _:
            raise ValueError("Unknown command. Use `bot`, `admin`, or `createsuperuser`.")

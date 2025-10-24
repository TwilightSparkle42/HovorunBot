"""Hovorun console entry point and commands.

This flat module is used by the `hovorun` console script and by `python -m AskBro` via __main__.

Commands:
- bot — start Telegram bot runtime
- admin — start admin FastAPI server
- createsuperuser — create or ensure the initial superuser exists

Usage examples:
- hovorun bot
- hovorun admin
- hovorun createsuperuser [-u USERNAME]

The same commands work when executed via a runner like `uv`.
"""
import importlib
import sys

from bot_runtime.runtime import BotRuntime
from di_config import setup_di
from management.superuser_service import SuperuserCreator, create_superuser_sync


def bot() -> None:
    """Start the Telegram bot runtime."""
    injector = setup_di()
    bot_runtime = injector.get(BotRuntime)
    bot_runtime.run()


def api() -> None:
    """Start the FastAPI admin server using uvicorn.

    Runs the ASGI app defined in ``admin_panel.app``.
    """
    uvicorn = importlib.import_module('uvicorn')
    _ = setup_di()  # ensure DI initialized; admin models may depend on it
    uvicorn.run('admin_panel.app:app', host='localhost', port=8000, reload=False)


def createsuperuser() -> None:
    """Create the first superuser and print the generated password, if created.

    Optional CLI arguments:
    - ``--username``, ``-u``  Override username (default: ``admin``)
    """
    injector = setup_di()
    creator = injector.get(SuperuserCreator)

    username = 'admin'
    args = sys.argv[2:]
    for i, arg in enumerate(args):
        if arg in {'--username', '-u'} and i + 1 < len(args):
            username = args[i + 1]
            break

    result = create_superuser_sync(creator, username=username)
    if result.created and result.password is not None:
        print(f'Superuser created: {result.username}\nPassword: {result.password}')
    else:
        print(f'Superuser already exists: {result.username}')


def main() -> None:
    """Console entry point.

    Commands:
    - ``bot`` — start Telegram bot runtime
    - ``admin`` — start admin FastAPI server
    - ``createsuperuser`` — create or ensure the initial superuser exists
    """
    if len(sys.argv) == 1:
        raise ValueError('Missing command. Use `bot`, `admin`, or `createsuperuser`.')

    cmd = sys.argv[1].lower()
    match cmd:
        case 'admin':
            api()
        case 'bot':
            bot()
        case 'createsuperuser':
            createsuperuser()
        case _:
            raise ValueError('Unknown command. Use `bot`, `admin`, or `createsuperuser`.')

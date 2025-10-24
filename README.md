# Hovorun Bot: AI Sidekick for Telegram Chats

## Overview
Hovorun Bot is a pre-alpha Telegram assistant that brings large language models straight into your chats for quick
knowledge lookups and collaborative problem solving.

## Installation & Setup
1. Install the project locally in editable mode (Python 3.14 + `uv`):

   ```bash
   uv pip install -e .
   ```

2. Start Valkey for message caching (requires Docker):

   ```bash
   docker compose up -d valkey
   ```

3. Configure the environment. Settings are driven by Pydantic Settings, so populate a `.env` file (for example, copy
   `example.env`) and adjust variables as needed.

4. Create a Telegram bot and grab its token via the
   [Telegram Bot API documentation](https://core.telegram.org/bots#3-how-do-i-create-a-bot), then set `TELEGRAM_TOKEN`
   in your environment.

## Usage
- Start the Telegram bot runtime (from your virtual environment or via `uv`):

  ```bash
  uv run hovorun bot
  ```

- Launch the FastAPI + FastAdmin panel:

  ```bash
  uv run hovorun admin
  ```

- Create or ensure the initial superuser exists:

  ```bash
  uv run hovorun createsuperuser --username admin
  ```

## Development
- Apply database migrations with Alembic when needed:

  ```bash
  uv run alembic upgrade head
  ```

- Run the test suite:

  ```bash
  uv run pytest
  ```

- Keep the codebase clean:

  ```bash
  uv run ruff check .
  uv run mypy .
  ```

## License
BSD 3-Clause License (see `LICENSE`).

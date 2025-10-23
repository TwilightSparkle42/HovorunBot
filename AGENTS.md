# Repository Guidelines

## Project Structure & Module Organization
The application entry point is `main.py`, which boots the dependency injector configured in `di_config.py`. 
Each independent component should be isolated in its own package or subpackage. Follow existing code as an example.
Keep new code modular and register injectable services in the appropriate `module.py`.

## Build, Test, and Development Commands
Any code must be validated using such tools as ruff and mypy, and all issues must be resolved. Ignoring of issues
is prohibited until there is an obvious reason for it. Use `uv` as an application entry point.

## Coding Style & Naming Conventions
Target Python 3.14 features and prefer type annotations everywhere. Do not use `from __future__ import annotations`.
Use four spaces for indentation, single quotes for short strings, and descriptive module-level names 
(e.g., `summarize_message_handler`). All subclasses must be named with parent class suffix (e.g., `MessageHandler`,
`MessageRepository` etc.).
Documentation should follow reStructuredText format.
Any txt file (e.g., README.md, AGENTS.md) should be written in English, unless it is a translation. They must be
human-readable with no lines extending more than 200 characters.

## Commit & Pull Request Guidelines
Use conventional commit strategy for commit messages. Describe reasoning the changes are made instead of code changes
themselves.

## Environment & Configuration Tips
Never store real credentials in example.env or any settings, except they are not secrets, like `askbro.db` name for
SQLite database.
Use docker containers if you need any external tool for the application, like `redis` or `valkey`
`alembic` is used for sqlalchemy database migrations

# Strict rules
Never commit any code without confirmation.
Never create migrations without confirmation.
Never apply migrations without confirmation.
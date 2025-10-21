# Repository Guidelines

## Project Structure & Module Organization
The application entry point is `main.py`, which boots the dependency injector configured in `di_config.py`. 
Each independent component should be isolated in its own package or subpackage. Follow existing one as an example.
Keep new code modular and register injectable services in the appropriate `module.py`.

## Build, Test, and Development Commands
Any code must be validated using such tools as ruff and mypy, and all issues must be resolved. Ignoring of issues
is prohibited until there is an obvious reason for it.

## Coding Style & Naming Conventions
Target Python 3.14 features and prefer type annotations everywhere. Do not use `from __future__ import annotations`.
Use four spaces for indentation, single quotes for short strings, and descriptive module-level names 
(e.g., `summarize_message_handler`). Service classes should end with `Service` or `Repository`; 
injector modules should expose a `Module` subclass in `module.py`.
Following PEP8 is recommended.
Documentation should follow reStructuredText format.

## Commit & Pull Request Guidelines
Use conventional commit strategy for commit messages. Describe reasoning the changes are made instead of code changes
themselves.

## Environment & Configuration Tips
Never store real credentials in example.env or any settings, except they are not secrets, like `askbro.db` name for
SQLite database.
Use docker containers if you need any external tool for the application, like `redis` or `valkey`
`alembic` is used for sqlalchemy database migrations
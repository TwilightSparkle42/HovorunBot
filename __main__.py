"""Module entry point for `python -m AskBro`.

Delegates to the top-level CLI implementation to keep a single source of truth
for command behavior while preserving a flat project structure.
"""

from cli import main

if __name__ == "__main__":
    main()

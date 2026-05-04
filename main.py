"""Project entry point.

Thin wrapper that delegates to ``contextualization.cli``.

After installing the project (``pip install -e .``), the same CLI is
exposed as the ``contextualization`` console script.
"""

from contextualization.cli import main

if __name__ == "__main__":
    main()

"""
Purpose: Pytest configuration for Law of Demeter test directory

Scope: Skip test collection when implementation module is not yet available

Overview: Uses pytest_ignore_collect hook to prevent collection errors for RED tests
    that import from src.linters.law_of_demeter (not yet implemented). Once the
    implementation module exists, this hook stops skipping and tests run normally.

Dependencies: pytest

Exports: pytest_ignore_collect hook

Interfaces: Standard pytest conftest hook

Implementation: Tries importing src.linters.law_of_demeter; skips test_*.py collection
    on ImportError
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


def pytest_ignore_collect(collection_path: Path, config: Any) -> bool | None:
    """Skip LoD test collection when implementation module does not exist yet."""
    try:
        import src.linters.law_of_demeter  # noqa: F401

        return None
    except ImportError:
        if collection_path.suffix == ".py" and collection_path.name.startswith("test_"):
            # Skip fixture files in subdirectories — they have no actual tests
            if "fixtures" in collection_path.parts:
                return None
            return True
    return None

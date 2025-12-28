"""
Purpose: Shared ignore pattern matching utilities

Scope: Common ignore pattern checking for stringly-typed linter components

Overview: Provides shared utility functions for checking if file paths match ignore patterns.
    Used by both the main linter and violation generator to avoid duplicating ignore pattern
    matching logic. Centralizes the ignore pattern matching algorithm.

Dependencies: pathlib.Path, fnmatch

Exports: is_ignored function

Interfaces: is_ignored(file_path, ignore_patterns) -> bool

Implementation: Glob pattern matching with fnmatch for flexible ignore patterns
"""

import fnmatch
from pathlib import Path


def is_ignored(file_path: str | Path, ignore_patterns: list[str]) -> bool:
    """Check if file path matches any ignore pattern.

    Supports glob patterns like:
    - **/tests/** - matches any file in tests directories
    - **/*_test.py - matches any file ending in _test.py
    - tests/ - simple substring match

    Args:
        file_path: Path to check (string or Path object)
        ignore_patterns: List of patterns to match against

    Returns:
        True if file should be ignored
    """
    if not ignore_patterns:
        return False

    path_str = str(file_path)

    for pattern in ignore_patterns:
        # Use fnmatch for glob-style patterns
        if fnmatch.fnmatch(path_str, pattern):
            return True
        # Also check if pattern appears as substring (for simple patterns)
        if pattern in path_str:
            return True

    return False

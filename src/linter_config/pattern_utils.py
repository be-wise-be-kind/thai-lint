"""
Purpose: Pattern matching utilities for file paths and content parsing

Scope: Gitignore-style pattern matching and content parsing

Overview: Provides utility functions for matching file paths against gitignore-style
    patterns and extracting patterns from configuration files. Supports directory
    patterns (trailing /), standard glob patterns via fnmatch, and comment filtering.

Dependencies: fnmatch for glob pattern matching, pathlib for path operations

Exports: matches_pattern, extract_patterns_from_content

Interfaces: matches_pattern(path, pattern) -> bool, extract_patterns_from_content(content) -> list

Implementation: fnmatch-based pattern matching with directory-aware logic
"""

import fnmatch
from pathlib import Path


def matches_pattern(path: str, pattern: str) -> bool:
    """Check if path matches gitignore-style pattern.

    Args:
        path: File path to check.
        pattern: Gitignore-style pattern.

    Returns:
        True if path matches pattern.
    """
    if pattern.endswith("/"):
        return _matches_directory_pattern(path, pattern)
    return fnmatch.fnmatch(path, pattern) or fnmatch.fnmatch(str(Path(path)), pattern)


def _matches_directory_pattern(path: str, pattern: str) -> bool:
    """Check if path matches a directory pattern (trailing /).

    Args:
        path: File path to check
        pattern: Directory pattern ending with /

    Returns:
        True if path is within the directory
    """
    dir_pattern = pattern.rstrip("/")
    path_parts = Path(path).parts
    if dir_pattern in path_parts:
        return True
    return fnmatch.fnmatch(path, dir_pattern + "*")


def extract_patterns_from_content(content: str) -> list[str]:
    """Extract non-empty, non-comment patterns from content.

    Args:
        content: File content with patterns (one per line)

    Returns:
        List of valid patterns (non-empty, non-comment lines)
    """
    lines = [line.strip() for line in content.splitlines()]
    return [line for line in lines if line and not line.startswith("#")]

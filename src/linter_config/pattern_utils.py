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
    return _segments_match(path.split("/"), pattern.split("/"))


def _segments_match(path_parts: list[str], pattern_parts: list[str]) -> bool:
    """Match path segments against pattern segments, "**" spanning zero or more segments.

    Matching is done component-by-component rather than as one fnmatch'd string, so a
    plain "*"/"?" in a pattern segment can never accidentally cross a "/" boundary -
    only a literal "**" segment may consume any number (including zero) of path
    segments. Whole-string fnmatch cannot express that distinction: "**/test_*.py"
    would otherwise match any ".py" file merely because some unrelated ancestor
    directory happened to contain "test_" (e.g. pytest's own tmp-dir naming).
    """
    if not pattern_parts:
        return not path_parts
    head, *rest_pattern = pattern_parts
    if head == "**":
        return _double_star_matches(path_parts, rest_pattern)
    return _literal_segment_matches(path_parts, head, rest_pattern)


def _double_star_matches(path_parts: list[str], rest_pattern: list[str]) -> bool:
    """Check whether a "**" can consume some prefix of path_parts to match the rest."""
    if not rest_pattern:
        return True
    return any(_segments_match(path_parts[i:], rest_pattern) for i in range(len(path_parts) + 1))


def _literal_segment_matches(path_parts: list[str], head: str, rest_pattern: list[str]) -> bool:
    """Check a single non-"**" pattern segment against the next path segment."""
    if not path_parts:
        return False
    if not fnmatch.fnmatch(path_parts[0], head):
        return False
    return _segments_match(path_parts[1:], rest_pattern)


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
    return fnmatch.fnmatch(path, dir_pattern + "/*")


def extract_patterns_from_content(content: str) -> list[str]:
    """Extract non-empty, non-comment patterns from content.

    Args:
        content: File content with patterns (one per line)

    Returns:
        List of valid patterns (non-empty, non-comment lines)
    """
    lines = [line.strip() for line in content.splitlines()]
    return [line for line in lines if line and not line.startswith("#")]

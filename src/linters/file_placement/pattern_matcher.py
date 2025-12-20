"""
Purpose: Pattern matching utilities for file placement linter

Scope: Handles regex pattern matching for allow/deny file placement rules

Overview: Provides pattern matching functionality for the file placement linter. Matches
    file paths against regex patterns for both allow and deny lists. Supports case-insensitive
    matching and extracts denial reasons from configuration. Isolates pattern matching logic
    from rule checking and configuration validation.

Dependencies: re

Exports: PatternMatcher

Interfaces: match_deny_patterns(path, patterns) -> (bool, reason), match_allow_patterns(path, patterns) -> bool

Implementation: Uses re.search() for pattern matching with IGNORECASE flag
"""

import re
from re import Pattern


class PatternMatcher:
    """Handles regex pattern matching for file paths."""

    def __init__(self) -> None:
        """Initialize the pattern matcher with compiled regex cache."""
        self._compiled_patterns: dict[str, Pattern[str]] = {}

    def _get_compiled(self, pattern: str) -> Pattern[str]:
        """Get compiled regex pattern, caching for reuse.

        Args:
            pattern: Regex pattern string

        Returns:
            Compiled regex Pattern object
        """
        if pattern not in self._compiled_patterns:
            self._compiled_patterns[pattern] = re.compile(pattern, re.IGNORECASE)
        return self._compiled_patterns[pattern]

    def match_deny_patterns(
        self, path_str: str, deny_patterns: list[dict[str, str]]
    ) -> tuple[bool, str | None]:
        """Check if path matches any deny patterns.

        Args:
            path_str: File path to check
            deny_patterns: List of deny pattern dicts with 'pattern' and 'reason'

        Returns:
            Tuple of (is_denied, reason)
        """
        for deny_item in deny_patterns:
            compiled = self._get_compiled(deny_item["pattern"])
            if compiled.search(path_str):
                reason = deny_item.get("reason", "File not allowed in this location")
                return True, reason
        return False, None

    def match_allow_patterns(self, path_str: str, allow_patterns: list[str]) -> bool:
        """Check if path matches any allow patterns.

        Args:
            path_str: File path to check
            allow_patterns: List of regex patterns

        Returns:
            True if path matches any pattern
        """
        return any(self._get_compiled(pattern).search(path_str) for pattern in allow_patterns)

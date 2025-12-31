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
from collections.abc import Sequence
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
        self, path_str: str, deny_patterns: Sequence[dict[str, str] | str]
    ) -> tuple[bool, str | None]:
        """Check if path matches any deny patterns.

        Args:
            path_str: File path to check
            deny_patterns: List of deny patterns (either dicts with 'pattern'/'reason'
                or plain regex strings for backward compatibility)

        Returns:
            Tuple of (is_denied, reason)
        """
        for deny_item in deny_patterns:
            pattern, reason = self._extract_pattern_and_reason(deny_item)
            compiled = self._get_compiled(pattern)
            if compiled.search(path_str):
                return True, reason
        return False, None

    def _extract_pattern_and_reason(self, deny_item: dict[str, str] | str) -> tuple[str, str]:
        """Extract pattern and reason from a deny item.

        Args:
            deny_item: Either a dict with 'pattern' key or a plain string pattern

        Returns:
            Tuple of (pattern, reason)
        """
        if isinstance(deny_item, str):
            return deny_item, "File not allowed in this location"
        return deny_item["pattern"], deny_item.get(
            "reason", deny_item.get("message", "File not allowed in this location")
        )

    def match_allow_patterns(self, path_str: str, allow_patterns: list[str]) -> bool:
        """Check if path matches any allow patterns.

        Args:
            path_str: File path to check
            allow_patterns: List of regex patterns

        Returns:
            True if path matches any pattern
        """
        return any(self._get_compiled(pattern).search(path_str) for pattern in allow_patterns)

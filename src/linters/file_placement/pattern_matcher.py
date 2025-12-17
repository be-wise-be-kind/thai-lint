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


class PatternMatcher:
    """Handles regex pattern matching for file paths."""

    def __init__(self) -> None:
        """Initialize the pattern matcher."""
        pass  # Stateless matcher for regex patterns

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
            pattern = deny_item["pattern"]
            if re.search(pattern, path_str, re.IGNORECASE):
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
        return any(re.search(pattern, path_str, re.IGNORECASE) for pattern in allow_patterns)

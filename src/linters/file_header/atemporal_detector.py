"""
Purpose: Detects temporal language patterns in file headers

Scope: File header validation for atemporal language compliance

Overview: Implements pattern-based detection of temporal language that violates atemporal
    documentation requirements. Detects dates, temporal qualifiers, state change language,
    and future references using regex patterns. Provides violation details for each pattern match.
    Uses four pattern categories (dates, temporal qualifiers, state changes, future references)
    to identify violations and returns detailed information for each match.

Dependencies: re module for regex-based pattern matching

Exports: AtemporalDetector class with detect_violations method

Interfaces: detect_violations(text) -> list[tuple[str, str, int]] returns pattern matches with line numbers

Implementation: Regex-based pattern matching with pre-compiled patterns organized by category

Suppressions:
    - nesting: detect_violations iterates over pattern categories and their patterns.
        Natural grouping by category requires nested loops.
"""

import re
from re import Pattern


def _compile_patterns(patterns: list[tuple[str, str]]) -> list[tuple[Pattern[str], str]]:
    """Compile regex patterns for efficient reuse."""
    return [(re.compile(pattern, re.IGNORECASE), desc) for pattern, desc in patterns]


class AtemporalDetector:
    """Detects temporal language patterns in text."""

    # Pre-compiled date patterns
    DATE_PATTERNS = _compile_patterns(
        [
            (r"\d{4}-\d{2}-\d{2}", "ISO date format (YYYY-MM-DD)"),
            (
                r"(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}",
                "Month Year format",
            ),
            (r"(?:Created|Updated|Modified):\s*\d{4}", "Date metadata"),
        ]
    )

    # Pre-compiled temporal qualifiers
    TEMPORAL_QUALIFIERS = _compile_patterns(
        [
            (r"\bcurrently\b", 'temporal qualifier "currently"'),
            (r"\bnow\b", 'temporal qualifier "now"'),
            (r"\brecently\b", 'temporal qualifier "recently"'),
            (r"\bsoon\b", 'temporal qualifier "soon"'),
            (r"\bfor now\b", 'temporal qualifier "for now"'),
        ]
    )

    # Pre-compiled state change language
    STATE_CHANGE = _compile_patterns(
        [
            (r"\breplaces?\b", 'state change "replaces"'),
            (r"\bmigrated from\b", 'state change "migrated from"'),
            (r"\bformerly\b", 'state change "formerly"'),
            (r"\bold implementation\b", 'state change "old"'),
            (r"\bnew implementation\b", 'state change "new"'),
        ]
    )

    # Pre-compiled future references
    FUTURE_REFS = _compile_patterns(
        [
            (r"\bwill be\b", 'future reference "will be"'),
            (r"\bplanned\b", 'future reference "planned"'),
            (r"\bto be added\b", 'future reference "to be added"'),
            (r"\bcoming soon\b", 'future reference "coming soon"'),
        ]
    )

    def detect_violations(  # thailint: ignore[nesting]
        self, text: str
    ) -> list[tuple[str, str, int]]:
        """Detect all temporal language violations in text.

        Args:
            text: Text to check for temporal language

        Returns:
            List of (pattern, description, line_number) tuples for each violation
        """
        violations = []

        # Check all pattern categories (patterns are pre-compiled)
        all_patterns = (
            self.DATE_PATTERNS + self.TEMPORAL_QUALIFIERS + self.STATE_CHANGE + self.FUTURE_REFS
        )

        lines = text.split("\n")
        for line_num, line in enumerate(lines, start=1):
            for compiled_pattern, description in all_patterns:
                if compiled_pattern.search(line):
                    violations.append((compiled_pattern.pattern, description, line_num))

        return violations

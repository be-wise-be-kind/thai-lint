"""
Purpose: Violation overlap filtering

Scope: Filters overlapping violations within same file

Overview: Filters overlapping violations by comparing line ranges. When violations are close together
    (within 3 lines), only the first one is kept. Used by ViolationDeduplicator to remove duplicate
    reports from rolling hash windows.

Dependencies: Violation

Exports: ViolationFilter class

Interfaces: ViolationFilter.filter_overlapping(sorted_violations)

Implementation: Iterates through sorted violations, keeps first of each overlapping group
"""

from src.core.types import Violation

# Default fallback for line count when parsing fails
DEFAULT_FALLBACK_LINE_COUNT = 5


class ViolationFilter:
    """Filters overlapping violations."""

    def __init__(self) -> None:
        """Initialize the violation filter."""
        pass  # Stateless filter for overlapping violations

    def filter_overlapping(self, sorted_violations: list[Violation]) -> list[Violation]:
        """Filter overlapping violations, keeping first occurrence.

        Args:
            sorted_violations: Violations sorted by line number

        Returns:
            Filtered list with overlaps removed
        """
        kept: list[Violation] = []
        for violation in sorted_violations:
            if not self._overlaps_any(violation, kept):
                kept.append(violation)
        return kept

    def _overlaps_any(self, violation: Violation, kept_violations: list[Violation]) -> bool:
        """Check if violation overlaps with any kept violations.

        Args:
            violation: Violation to check
            kept_violations: Previously kept violations

        Returns:
            True if violation overlaps with any kept violation
        """
        for kept in kept_violations:
            if self._overlaps(violation, kept):
                return True
        return False

    def _overlaps(self, v1: Violation, v2: Violation) -> bool:
        """Check if two violations overlap.

        Args:
            v1: First violation (later line number)
            v2: Second violation (earlier line number)

        Returns:
            True if violations overlap based on code block size
        """
        line1 = v1.line or 0
        line2 = v2.line or 0

        # Extract line count from message format: "Duplicate code (N lines, ...)"
        line_count = self._extract_line_count(v1.message)

        # Blocks overlap if their line ranges intersect
        # Block at line2 covers [line2, line2 + line_count - 1]
        # Block at line1 overlaps if line1 < line2 + line_count
        return line1 < line2 + line_count

    def _extract_line_count(self, message: str) -> int:
        """Extract line count from violation message.

        Args:
            message: Violation message containing line count

        Returns:
            Number of lines in the duplicate code block (default 5 if not found)
        """
        # Message format: "Duplicate code (5 lines, 2 occurrences)..."
        try:
            start = message.index("(") + 1
            end = message.index(" lines")
            return int(message[start:end])
        except (ValueError, IndexError):
            return DEFAULT_FALLBACK_LINE_COUNT  # Default fallback

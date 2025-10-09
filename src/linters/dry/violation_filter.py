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


class ViolationFilter:
    """Filters overlapping violations."""

    def filter_overlapping(self, sorted_violations: list[Violation]) -> list[Violation]:
        """Filter overlapping violations, keeping first occurrence.

        Args:
            sorted_violations: Violations sorted by line number

        Returns:
            Filtered list with overlaps removed
        """
        kept = []
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
            v1: First violation
            v2: Second violation

        Returns:
            True if violations overlap (within 3 lines)
        """
        line1 = v1.line or 0
        line2 = v2.line or 0
        return line1 <= line2 + 2

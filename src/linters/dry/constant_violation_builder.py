"""
Purpose: Build violation messages for duplicate constants

Scope: Violation message formatting for constant duplication detection

Overview: Formats detailed violation messages for duplicate constant detection. Creates messages
    that include the constant name(s), all file locations with line numbers, and the values
    assigned at each location. Distinguishes between exact matches (same constant name) and
    fuzzy matches (similar names like API_TIMEOUT and TIMEOUT_API). Provides actionable guidance
    to consolidate constants into a shared module.

Dependencies: ConstantGroup from constant module, Violation from core.types

Exports: ConstantViolationBuilder class

Interfaces: ConstantViolationBuilder.build_violations(groups, rule_id) -> list[Violation]

Implementation: Message template formatting with location enumeration and fuzzy match indication
"""

from src.core.types import Severity, Violation

from .constant import ConstantGroup, ConstantLocation

# Maximum other locations to show in violation message
MAX_DISPLAYED_LOCATIONS = 3


class ConstantViolationBuilder:
    """Builds violation messages for duplicate constants."""

    def __init__(self, min_occurrences: int = 2) -> None:
        """Initialize with minimum occurrence threshold."""
        self.min_occurrences = min_occurrences

    def build_violations(self, groups: list[ConstantGroup], rule_id: str) -> list[Violation]:
        """Build violations from constant groups."""
        violations = []
        for group in groups:
            if group.file_count >= self.min_occurrences:
                violations.extend(self._violations_for_group(group, rule_id))
        return violations

    def _violations_for_group(self, group: ConstantGroup, rule_id: str) -> list[Violation]:
        """Create violations for all locations in a group."""
        return [
            Violation(
                rule_id=rule_id,
                file_path=str(loc.file_path),
                line=loc.line_number,
                column=1,
                message=self._format_message(group, loc),
                severity=Severity.ERROR,
            )
            for loc in group.locations
        ]

    def _format_message(self, group: ConstantGroup, current: ConstantLocation) -> str:
        """Format the violation message based on match type."""
        others = _get_other_locations(group, current)
        locations_text = _format_locations_text(others)
        if group.is_fuzzy_match:
            names_str = " ≈ ".join(f"'{n}'" for n in sorted(group.all_names))
            return (
                f"Similar constants found: {names_str} in {group.file_count} files. "
                f"{locations_text} "
                f"These appear to represent the same concept - consider standardizing the name."
            )
        return (
            f"Duplicate constant '{group.canonical_name}' defined in {group.file_count} files. "
            f"{locations_text} "
            f"Consider consolidating to a shared constants module."
        )


def _get_other_locations(group: ConstantGroup, current: ConstantLocation) -> list[ConstantLocation]:
    """Get locations excluding current (module-level helper)."""
    return [
        loc
        for loc in group.locations
        if loc.file_path != current.file_path or loc.line_number != current.line_number
    ]


def _format_locations_text(others: list[ConstantLocation]) -> str:
    """Format other locations as text (module-level helper)."""
    if not others:
        return ""
    parts = [_format_single_location(loc) for loc in others[:MAX_DISPLAYED_LOCATIONS]]
    result = "Also found in: " + ", ".join(parts)
    extra = len(others) - MAX_DISPLAYED_LOCATIONS
    return result + (f" and {extra} more." if extra > 0 else ".")


def _format_single_location(loc: ConstantLocation) -> str:
    """Format a single location for display (module-level helper)."""
    value_str = f" = {loc.value}" if loc.value else ""
    return f"{loc.file_path.name}:{loc.line_number} ({loc.name}{value_str})"

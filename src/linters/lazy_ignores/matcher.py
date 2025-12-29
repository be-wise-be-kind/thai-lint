"""
Purpose: Cross-reference matcher for lazy-ignores linter

Scope: Matching ignore directives with header suppressions

Overview: Provides IgnoreSuppressionMatcher class that cross-references linting ignore
    directives found in code with Suppressions entries declared in file headers. Handles
    case-insensitive rule ID normalization and special patterns like type:ignore[code].
    Identifies unjustified ignores (code ignores without header entries) and orphaned
    suppressions (header entries without matching code ignores).

Dependencies: SuppressionsParser for normalization, types for IgnoreDirective and IgnoreType

Exports: IgnoreSuppressionMatcher

Interfaces: find_unjustified(), find_orphaned()

Implementation: Set-based matching with rule ID normalization for case-insensitive comparison
"""

from .header_parser import SuppressionsParser
from .types import IgnoreDirective, IgnoreType


class IgnoreSuppressionMatcher:
    """Matches ignore directives with header suppressions."""

    def __init__(self, parser: SuppressionsParser) -> None:
        """Initialize the matcher.

        Args:
            parser: SuppressionsParser for rule ID normalization.
        """
        self._parser = parser

    def collect_used_rule_ids(self, ignores: list[IgnoreDirective]) -> set[str]:
        """Collect all normalized rule IDs used in ignore directives.

        Args:
            ignores: List of ignore directives from code.

        Returns:
            Set of normalized rule IDs that have ignore directives.
        """
        used: set[str] = set()
        for ignore in ignores:
            used.update(self._get_matchable_rule_ids(ignore))
        return used

    def _get_matchable_rule_ids(self, ignore: IgnoreDirective) -> list[str]:
        """Get normalized rule IDs for matching, handling special formats.

        For type:ignore directives, generates both the raw rule_id and
        the full type:ignore[rule_id] format for header matching.

        Args:
            ignore: The ignore directive to extract rule IDs from.

        Returns:
            List of normalized rule IDs for matching.
        """
        if not ignore.rule_ids:
            # Bare ignores (no rule IDs) are tracked by their type
            return [self._normalize(ignore.ignore_type.value)]

        ids: list[str] = []
        for rule_id in ignore.rule_ids:
            normalized = self._normalize(rule_id)
            ids.append(normalized)

            # For type:ignore, also add the full format for header matching
            if ignore.ignore_type == IgnoreType.TYPE_IGNORE:
                full_format = f"type:ignore[{normalized}]"
                ids.append(full_format)

        return ids

    def find_unjustified_rule_ids(
        self, ignore: IgnoreDirective, suppressions: dict[str, str]
    ) -> list[str]:
        """Find which rule IDs in an ignore are not justified.

        Args:
            ignore: The ignore directive to check.
            suppressions: Dict of normalized rule IDs to justifications.

        Returns:
            List of unjustified rule IDs (original case preserved).
        """
        if not ignore.rule_ids:
            # Bare ignore (e.g., # noqa without rules) - check by type
            type_key = self._normalize(ignore.ignore_type.value)
            if type_key not in suppressions:
                return [ignore.ignore_type.value]
            return []

        # Check each specific rule ID
        unjustified: list[str] = []
        for rule_id in ignore.rule_ids:
            if not self._is_rule_justified(ignore, rule_id, suppressions):
                unjustified.append(rule_id)
        return unjustified

    def _is_rule_justified(
        self, ignore: IgnoreDirective, rule_id: str, suppressions: dict[str, str]
    ) -> bool:
        """Check if a specific rule ID is justified in suppressions.

        Args:
            ignore: The ignore directive containing this rule.
            rule_id: The rule ID to check.
            suppressions: Dict of normalized rule IDs to justifications.

        Returns:
            True if the rule has a matching suppression entry.
        """
        normalized = self._normalize(rule_id)

        # Direct match
        if normalized in suppressions:
            return True

        # For type:ignore, also check the full format
        if ignore.ignore_type == IgnoreType.TYPE_IGNORE:
            full_format = f"type:ignore[{normalized}]"
            if full_format in suppressions:
                return True

        return False

    def find_orphaned_rule_ids(
        self, suppressions: dict[str, str], used_rule_ids: set[str]
    ) -> list[tuple[str, str]]:
        """Find header suppressions without matching code ignores.

        Args:
            suppressions: Dict mapping normalized rule IDs to justifications.
            used_rule_ids: Set of normalized rule IDs used in code.

        Returns:
            List of (rule_id, justification) tuples for orphaned suppressions.
        """
        orphaned: list[tuple[str, str]] = []
        for rule_id, justification in suppressions.items():
            if rule_id not in used_rule_ids:
                orphaned.append((rule_id.upper(), justification))
        return orphaned

    def _normalize(self, rule_id: str) -> str:
        """Normalize a rule ID for case-insensitive matching.

        Args:
            rule_id: The rule ID to normalize.

        Returns:
            Lowercase rule ID.
        """
        return self._parser.normalize_rule_id(rule_id)

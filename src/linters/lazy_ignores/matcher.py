"""
Purpose: Cross-reference matcher for lazy-ignores linter

Scope: Matching ignore directives with header suppressions

Overview: Provides IgnoreSuppressionMatcher class that cross-references linting ignore
    directives found in code with Suppressions entries declared in file headers. Handles
    case-insensitive rule ID normalization and special patterns like type:ignore[code].
    Identifies unjustified ignores (code ignores without header entries) and orphaned
    suppressions (header entries without matching code ignores).

Dependencies: SuppressionsParser for normalization, types for IgnoreDirective and IgnoreType,
    rule_id_utils for pure parsing functions

Exports: IgnoreSuppressionMatcher

Interfaces: find_unjustified(), find_orphaned()

Implementation: Set-based matching with rule ID normalization for case-insensitive comparison
"""

from .header_parser import SuppressionsParser
from .rule_id_utils import (
    comma_list_has_used_rule,
    find_rule_in_suppressions,
    is_type_ignore_format_in_suppressions,
    type_ignore_bracket_has_used_rule,
)
from .types import IgnoreDirective, IgnoreType


class IgnoreSuppressionMatcher:
    """Matches ignore directives with header suppressions."""

    def __init__(self, parser: SuppressionsParser, min_justification_length: int = 10) -> None:
        """Initialize the matcher.

        Args:
            parser: SuppressionsParser for rule ID normalization.
            min_justification_length: Minimum length for valid inline justification.
        """
        self._parser = parser
        self._min_justification_length = min_justification_length

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
        """Get normalized rule IDs for matching, handling special formats."""
        if not ignore.rule_ids:
            return [self._normalize(ignore.ignore_type.value)]

        ids: list[str] = []
        for rule_id in ignore.rule_ids:
            normalized = self._normalize(rule_id)
            ids.append(normalized)
            if ignore.ignore_type == IgnoreType.TYPE_IGNORE:
                ids.append(f"type:ignore[{normalized}]")
        return ids

    def find_unjustified_rule_ids(
        self, ignore: IgnoreDirective, suppressions: dict[str, str]
    ) -> list[str]:
        """Find which rule IDs in an ignore are not justified.

        Checks inline justification first (higher precedence), then falls back
        to header-based suppressions.

        Args:
            ignore: The ignore directive to check.
            suppressions: Dict of normalized rule IDs to justifications.

        Returns:
            List of unjustified rule IDs (original case preserved).
        """
        if self._has_valid_inline_justification(ignore):
            return []

        if not ignore.rule_ids:
            return self._check_bare_ignore(ignore, suppressions)

        return self._check_rule_specific_ignore(ignore, suppressions)

    def _check_bare_ignore(
        self, ignore: IgnoreDirective, suppressions: dict[str, str]
    ) -> list[str]:
        """Check if a bare ignore (no specific rules) is justified."""
        type_key = self._normalize(ignore.ignore_type.value)
        if type_key in suppressions:
            return []
        return [ignore.ignore_type.value]

    def _check_rule_specific_ignore(
        self, ignore: IgnoreDirective, suppressions: dict[str, str]
    ) -> list[str]:
        """Check which specific rule IDs are not justified."""
        return [
            rule_id
            for rule_id in ignore.rule_ids
            if not self._is_rule_justified(ignore, rule_id, suppressions)
        ]

    def _has_valid_inline_justification(self, ignore: IgnoreDirective) -> bool:
        """Check if the ignore has a valid inline justification.

        Args:
            ignore: The ignore directive to check.

        Returns:
            True if the ignore has an inline justification meeting minimum length.
        """
        if not ignore.inline_justification:
            return False
        return len(ignore.inline_justification) >= self._min_justification_length

    def _is_rule_justified(
        self, ignore: IgnoreDirective, rule_id: str, suppressions: dict[str, str]
    ) -> bool:
        """Check if a specific rule ID is justified in suppressions."""
        normalized = self._normalize(rule_id)
        is_type_ignore = ignore.ignore_type == IgnoreType.TYPE_IGNORE

        if normalized in suppressions:
            return True
        if is_type_ignore and is_type_ignore_format_in_suppressions(normalized, suppressions):
            return True
        return find_rule_in_suppressions(normalized, suppressions, is_type_ignore)

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
            if not self._suppression_is_used(rule_id, used_rule_ids):
                orphaned.append((rule_id.upper(), justification))
        return orphaned

    def _suppression_is_used(self, suppression_key: str, used_rule_ids: set[str]) -> bool:
        """Check if a suppression key is used by any code ignores."""
        if suppression_key in used_rule_ids:
            return True
        if comma_list_has_used_rule(suppression_key, used_rule_ids):
            return True
        return type_ignore_bracket_has_used_rule(suppression_key, used_rule_ids)

    def _normalize(self, rule_id: str) -> str:
        """Normalize a rule ID for case-insensitive matching."""
        return self._parser.normalize_rule_id(rule_id)

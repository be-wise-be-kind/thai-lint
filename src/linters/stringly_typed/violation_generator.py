"""
Purpose: Violation generation from cross-file stringly-typed patterns

Scope: Generates violations from duplicate pattern hashes across files

Overview: Handles violation generation for stringly-typed patterns that appear across multiple
    files. Queries storage for duplicate hashes, retrieves patterns for each hash, builds
    violations with cross-references to other files, and filters patterns based on enum value
    thresholds. Separates violation generation logic from main linter rule to maintain SRP
    compliance.

Dependencies: StringlyTypedStorage, StoredPattern, StringlyTypedConfig, Violation, Severity

Exports: ViolationGenerator class

Interfaces: ViolationGenerator.generate_violations(storage, rule_id, config) -> list[Violation]

Implementation: Queries storage, validates pattern thresholds, builds violations with
    cross-file references
"""

from src.core.types import Severity, Violation

from .config import StringlyTypedConfig
from .ignore_utils import is_ignored
from .storage import StoredPattern, StringlyTypedStorage


def _filter_by_ignore(violations: list[Violation], ignore: list[str]) -> list[Violation]:
    """Filter violations by ignore patterns."""
    if not ignore:
        return violations
    return [v for v in violations if not is_ignored(v.file_path, ignore)]


class ViolationGenerator:
    """Generates violations from cross-file stringly-typed patterns."""

    def generate_violations(
        self,
        storage: StringlyTypedStorage,
        rule_id: str,
        config: StringlyTypedConfig,
    ) -> list[Violation]:
        """Generate violations from storage.

        Args:
            storage: Pattern storage instance
            rule_id: Rule identifier for violations
            config: Stringly-typed configuration with thresholds

        Returns:
            List of violations for patterns appearing in multiple files
        """
        duplicate_hashes = storage.get_duplicate_hashes(min_files=config.min_occurrences)
        violations: list[Violation] = []

        for hash_value in duplicate_hashes:
            patterns = storage.get_patterns_by_hash(hash_value)
            if self._should_skip_patterns(patterns, config):
                continue
            violations.extend(self._build_violation(p, patterns, rule_id) for p in patterns)

        return _filter_by_ignore(violations, config.ignore)

    def _should_skip_patterns(
        self, patterns: list[StoredPattern], config: StringlyTypedConfig
    ) -> bool:
        """Check if pattern group should be skipped based on config.

        Args:
            patterns: List of patterns with same hash
            config: Configuration with thresholds

        Returns:
            True if patterns should be skipped
        """
        if not patterns:
            return True
        first = patterns[0]
        return not self._is_enum_candidate(first, config) or self._is_allowed_string_set(
            first, config
        )

    def _is_enum_candidate(self, pattern: StoredPattern, config: StringlyTypedConfig) -> bool:
        """Check if pattern's value count is within enum range.

        Args:
            pattern: Pattern to check
            config: Configuration with enum thresholds

        Returns:
            True if value count is suitable for enum suggestion
        """
        value_count = len(pattern.string_values)
        return config.min_values_for_enum <= value_count <= config.max_values_for_enum

    def _is_allowed_string_set(self, pattern: StoredPattern, config: StringlyTypedConfig) -> bool:
        """Check if pattern's string set is in allowed list.

        Args:
            pattern: Pattern to check
            config: Configuration with allowed string sets

        Returns:
            True if string set is explicitly allowed
        """
        pattern_set = set(pattern.string_values)
        for allowed_set in config.allowed_string_sets:
            if pattern_set == set(allowed_set):
                return True
        return False

    def _build_violation(
        self,
        pattern: StoredPattern,
        all_patterns: list[StoredPattern],
        rule_id: str,
    ) -> Violation:
        """Build a violation for a pattern with cross-references.

        Args:
            pattern: The pattern to create violation for
            all_patterns: All patterns with same hash (for cross-references)
            rule_id: Rule identifier

        Returns:
            Violation instance
        """
        message = self._build_message(pattern, all_patterns)
        suggestion = self._build_suggestion(pattern)

        return Violation(
            rule_id=rule_id,
            file_path=str(pattern.file_path),
            line=pattern.line_number,
            column=pattern.column,
            message=message,
            severity=Severity.ERROR,
            suggestion=suggestion,
        )

    def _build_message(self, pattern: StoredPattern, all_patterns: list[StoredPattern]) -> str:
        """Build violation message with cross-file references.

        Args:
            pattern: The primary pattern
            all_patterns: All patterns with same hash

        Returns:
            Human-readable violation message
        """
        # Get unique file count
        file_count = len({p.file_path for p in all_patterns})

        # Format string values
        values_str = ", ".join(f"'{v}'" for v in sorted(pattern.string_values))

        # Build cross-references (excluding current file)
        other_refs = self._build_cross_references(pattern, all_patterns)

        message = (
            f"Stringly-typed pattern with values [{values_str}] appears in {file_count} files."
        )

        if other_refs:
            message += f" Also found in: {other_refs}."

        return message

    def _build_cross_references(
        self, pattern: StoredPattern, all_patterns: list[StoredPattern]
    ) -> str:
        """Build cross-reference string for other files.

        Args:
            pattern: Current pattern
            all_patterns: All patterns with same hash

        Returns:
            Comma-separated list of file:line references
        """
        refs = []
        for other in all_patterns:
            if other.file_path != pattern.file_path:
                refs.append(f"{other.file_path.name}:{other.line_number}")

        return ", ".join(refs)

    def _build_suggestion(self, pattern: StoredPattern) -> str:
        """Build fix suggestion for the pattern.

        Args:
            pattern: The pattern to suggest fix for

        Returns:
            Human-readable suggestion
        """
        values_count = len(pattern.string_values)
        var_info = f" for '{pattern.variable_name}'" if pattern.variable_name else ""

        return (
            f"Consider defining an enum or type union{var_info} with the "
            f"{values_count} possible values instead of using string literals."
        )

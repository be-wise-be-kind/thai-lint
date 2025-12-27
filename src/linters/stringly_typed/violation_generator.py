"""
Purpose: Violation generation from cross-file stringly-typed patterns

Scope: Generates violations from duplicate pattern hashes and function call patterns

Overview: Handles violation generation for stringly-typed patterns that appear across multiple
    files. Queries storage for duplicate hashes, retrieves patterns for each hash, builds
    violations with cross-references to other files, and filters patterns based on enum value
    thresholds. Delegates function call violation generation to FunctionCallViolationBuilder.
    Separates violation generation logic from main linter rule to maintain SRP compliance.

Dependencies: StringlyTypedStorage, StoredPattern, StringlyTypedConfig, Violation, Severity,
    FunctionCallViolationBuilder

Exports: ViolationGenerator class

Interfaces: ViolationGenerator.generate_violations(storage, rule_id, config) -> list[Violation]

Implementation: Queries storage, validates pattern thresholds, builds violations with
    cross-file references, delegates function call violations to builder
"""

from src.core.types import Severity, Violation

from .config import StringlyTypedConfig
from .context_filter import FunctionCallFilter
from .function_call_violation_builder import FunctionCallViolationBuilder
from .ignore_utils import is_ignored
from .storage import StoredPattern, StringlyTypedStorage


def _filter_by_ignore(violations: list[Violation], ignore: list[str]) -> list[Violation]:
    """Filter violations by ignore patterns."""
    if not ignore:
        return violations
    return [v for v in violations if not is_ignored(v.file_path, ignore)]


def _is_allowed_value_set(values: set[str], config: StringlyTypedConfig) -> bool:
    """Check if a set of values is in the allowed list."""
    return any(values == set(allowed) for allowed in config.allowed_string_sets)


class ViolationGenerator:  # thailint: ignore srp
    """Generates violations from cross-file stringly-typed patterns."""

    def __init__(self) -> None:
        """Initialize with helper builders and filters."""
        self._call_builder = FunctionCallViolationBuilder()
        self._call_filter = FunctionCallFilter()

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
        violations: list[Violation] = []
        violations.extend(self._generate_pattern_violations(storage, rule_id, config))
        violations.extend(self._generate_function_call_violations(storage, config))

        return _filter_by_ignore(violations, config.ignore)

    def _generate_pattern_violations(
        self,
        storage: StringlyTypedStorage,
        rule_id: str,
        config: StringlyTypedConfig,
    ) -> list[Violation]:
        """Generate violations for duplicate validation patterns."""
        duplicate_hashes = storage.get_duplicate_hashes(min_files=config.min_occurrences)
        violations: list[Violation] = []

        for hash_value in duplicate_hashes:
            patterns = storage.get_patterns_by_hash(hash_value)
            if self._should_skip_patterns(patterns, config):
                continue
            violations.extend(self._build_violation(p, patterns, rule_id) for p in patterns)

        return violations

    def _generate_function_call_violations(
        self,
        storage: StringlyTypedStorage,
        config: StringlyTypedConfig,
    ) -> list[Violation]:
        """Generate violations for function call patterns."""
        min_files = config.min_occurrences if config.require_cross_file else 1
        limited_funcs = storage.get_limited_value_functions(
            min_values=config.min_values_for_enum,
            max_values=config.max_values_for_enum,
            min_files=min_files,
        )

        violations: list[Violation] = []
        for function_name, param_index, unique_values in limited_funcs:
            if _is_allowed_value_set(unique_values, config):
                continue
            # Apply context-aware filtering to reduce false positives
            if not self._call_filter.should_include(function_name, param_index, unique_values):
                continue
            calls = storage.get_calls_by_function(function_name, param_index)
            violations.extend(self._call_builder.build_violations(calls, unique_values))

        return violations

    def _should_skip_patterns(
        self, patterns: list[StoredPattern], config: StringlyTypedConfig
    ) -> bool:
        """Check if pattern group should be skipped based on config."""
        if not patterns:
            return True
        first = patterns[0]
        if not self._is_enum_candidate(first, config):
            return True
        if self._is_pattern_allowed(first, config):
            return True
        # Skip if all values match excluded patterns (numeric strings, etc.)
        if self._call_filter.are_all_values_excluded(set(first.string_values)):
            return True
        return False

    def _is_enum_candidate(self, pattern: StoredPattern, config: StringlyTypedConfig) -> bool:
        """Check if pattern's value count is within enum range."""
        value_count = len(pattern.string_values)
        return config.min_values_for_enum <= value_count <= config.max_values_for_enum

    def _is_pattern_allowed(self, pattern: StoredPattern, config: StringlyTypedConfig) -> bool:
        """Check if pattern's string set is in allowed list."""
        return _is_allowed_value_set(set(pattern.string_values), config)

    def _build_violation(
        self, pattern: StoredPattern, all_patterns: list[StoredPattern], rule_id: str
    ) -> Violation:
        """Build a violation for a pattern with cross-references."""
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
        """Build violation message with cross-file references."""
        file_count = len({p.file_path for p in all_patterns})
        values_str = ", ".join(f"'{v}'" for v in sorted(pattern.string_values))
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
        """Build cross-reference string for other files."""
        refs = [
            f"{other.file_path.name}:{other.line_number}"
            for other in all_patterns
            if other.file_path != pattern.file_path
        ]
        return ", ".join(refs)

    def _build_suggestion(self, pattern: StoredPattern) -> str:
        """Build fix suggestion for the pattern."""
        values_count = len(pattern.string_values)
        var_info = f" for '{pattern.variable_name}'" if pattern.variable_name else ""

        return (
            f"Consider defining an enum or type union{var_info} with the "
            f"{values_count} possible values instead of using string literals."
        )

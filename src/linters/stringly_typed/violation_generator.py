"""
Purpose: Violation generation from cross-file stringly-typed patterns

Scope: Generates violations from duplicate pattern hashes, function call patterns, and
    scattered string comparisons

Overview: Handles violation generation for stringly-typed patterns that appear across multiple
    files. Queries storage for duplicate hashes, retrieves patterns for each hash, builds
    violations with cross-references to other files, and filters patterns based on enum value
    thresholds. Delegates function call violation generation to FunctionCallViolationBuilder.
    Generates violations for scattered string comparisons (e.g., `if env == "production"`)
    where a variable is compared to multiple unique string values across files.
    Applies inline ignore directives via IgnoreChecker to filter suppressed violations.
    Separates violation generation logic from main linter rule to maintain SRP compliance.

Dependencies: StringlyTypedStorage, StoredPattern, StoredComparison, StringlyTypedConfig,
    Violation, Severity, build_function_call_violations, IgnoreChecker

Exports: ViolationGenerator class, pure helper functions for message building

Interfaces: ViolationGenerator.generate_violations(storage, rule_id, config) -> list[Violation]

Implementation: Queries storage, validates pattern thresholds, builds violations with
    cross-file references, delegates function call violations to builder, generates
    comparison violations from scattered string comparisons, filters by ignore directives

Suppressions:
    - too-many-arguments,too-many-positional-arguments: _process_variable helper passes
        accumulated state (storage, config, covered_variables, violations) to avoid
        global state or complex return types
"""

from src.core.types import Severity, Violation

from . import context_filter
from .config import StringlyTypedConfig
from .function_call_violation_builder import build_function_call_violations
from .ignore_checker import IgnoreChecker
from .ignore_utils import is_ignored
from .storage import StoredComparison, StoredPattern, StringlyTypedStorage

# --- Pure helper functions for filtering ---


def _filter_by_ignore(violations: list[Violation], ignore: list[str]) -> list[Violation]:
    """Filter violations by ignore patterns."""
    if not ignore:
        return violations
    return [v for v in violations if not is_ignored(v.file_path, ignore)]


def _is_allowed_value_set(values: set[str], config: StringlyTypedConfig) -> bool:
    """Check if a set of values is in the allowed list."""
    return any(values == set(allowed) for allowed in config.allowed_string_sets)


def _is_enum_candidate(pattern: StoredPattern, config: StringlyTypedConfig) -> bool:
    """Check if pattern's value count is within enum range."""
    value_count = len(pattern.string_values)
    return config.min_values_for_enum <= value_count <= config.max_values_for_enum


def _is_pattern_allowed(pattern: StoredPattern, config: StringlyTypedConfig) -> bool:
    """Check if pattern's string set is in allowed list."""
    return _is_allowed_value_set(set(pattern.string_values), config)


def _should_skip_patterns(patterns: list[StoredPattern], config: StringlyTypedConfig) -> bool:
    """Check if pattern group should be skipped based on config."""
    if not patterns:
        return True
    first = patterns[0]
    if not _is_enum_candidate(first, config):
        return True
    if _is_pattern_allowed(first, config):
        return True
    # Skip if all values match excluded patterns (numeric strings, etc.)
    if context_filter.are_all_values_excluded(set(first.string_values)):
        return True
    return False


def _should_skip_comparison(unique_values: set[str], config: StringlyTypedConfig) -> bool:
    """Check if a comparison pattern should be skipped based on config."""
    if len(unique_values) > config.max_values_for_enum:
        return True
    if _is_allowed_value_set(unique_values, config):
        return True
    if context_filter.are_all_values_excluded(unique_values):
        return True
    return False


# Variable suffixes that indicate false positive comparisons
_EXCLUDED_VARIABLE_SUFFIXES: tuple[str, ...] = (
    ".value",  # Enum value access
    ".method",  # HTTP method
    ".type",  # Tree-sitter node types
)


def _should_skip_variable(variable_name: str) -> bool:
    """Check if a variable name indicates a false positive comparison."""
    # Check excluded suffixes
    if any(variable_name.endswith(s) for s in _EXCLUDED_VARIABLE_SUFFIXES):
        return True
    # Test assertion patterns (underscore prefix is common in comprehensions/lambdas)
    return variable_name.startswith("_.")


# --- Pure helper functions for message building ---


def _build_cross_references(pattern: StoredPattern, all_patterns: list[StoredPattern]) -> str:
    """Build cross-reference string for other files."""
    refs = [
        f"{other.file_path.name}:{other.line_number}"
        for other in all_patterns
        if other.file_path != pattern.file_path
    ]
    return ", ".join(refs)


def _build_message(pattern: StoredPattern, all_patterns: list[StoredPattern]) -> str:
    """Build violation message with cross-file references."""
    file_count = len({p.file_path for p in all_patterns})
    values_str = ", ".join(f"'{v}'" for v in sorted(pattern.string_values))
    other_refs = _build_cross_references(pattern, all_patterns)

    message = f"Stringly-typed pattern with values [{values_str}] appears in {file_count} files."
    if other_refs:
        message += f" Also found in: {other_refs}."

    return message


def _build_suggestion(pattern: StoredPattern) -> str:
    """Build fix suggestion for the pattern."""
    values_count = len(pattern.string_values)
    var_info = f" for '{pattern.variable_name}'" if pattern.variable_name else ""

    return (
        f"Consider defining an enum or type union{var_info} with the "
        f"{values_count} possible values instead of using string literals."
    )


def _build_comparison_cross_references(
    comparison: StoredComparison,
    all_comparisons: list[StoredComparison],
) -> str:
    """Build cross-reference string for other comparison locations."""
    refs = [
        f"{other.file_path.name}:{other.line_number}"
        for other in all_comparisons
        if other.file_path != comparison.file_path
    ]
    return ", ".join(refs)


def _build_comparison_message(
    comparison: StoredComparison,
    all_comparisons: list[StoredComparison],
    unique_values: set[str],
) -> str:
    """Build violation message for scattered comparison."""
    file_count = len({c.file_path for c in all_comparisons})
    values_str = ", ".join(f"'{v}'" for v in sorted(unique_values))
    other_refs = _build_comparison_cross_references(comparison, all_comparisons)

    message = (
        f"Variable '{comparison.variable_name}' is compared to {len(unique_values)} "
        f"different string values [{values_str}] across {file_count} file(s)."
    )
    if other_refs:
        message += f" Also compared in: {other_refs}."

    return message


def _build_comparison_suggestion(comparison: StoredComparison, unique_values: set[str]) -> str:
    """Build fix suggestion for scattered comparison."""
    return (
        f"Consider defining an enum for '{comparison.variable_name}' with the "
        f"{len(unique_values)} possible values instead of using string literals "
        f"in scattered comparisons."
    )


# --- Pure helper function for violation building ---


def _build_violation(
    pattern: StoredPattern, all_patterns: list[StoredPattern], rule_id: str
) -> Violation:
    """Build a violation for a pattern with cross-references."""
    message = _build_message(pattern, all_patterns)
    suggestion = _build_suggestion(pattern)

    return Violation(
        rule_id=rule_id,
        file_path=str(pattern.file_path),
        line=pattern.line_number,
        column=pattern.column,
        message=message,
        severity=Severity.ERROR,
        suggestion=suggestion,
    )


def _build_comparison_violation(
    comparison: StoredComparison,
    all_comparisons: list[StoredComparison],
    unique_values: set[str],
) -> Violation:
    """Build a violation for a scattered string comparison."""
    message = _build_comparison_message(comparison, all_comparisons, unique_values)
    suggestion = _build_comparison_suggestion(comparison, unique_values)

    return Violation(
        rule_id="stringly-typed.scattered-comparison",
        file_path=str(comparison.file_path),
        line=comparison.line_number,
        column=comparison.column,
        message=message,
        severity=Severity.ERROR,
        suggestion=suggestion,
    )


# --- Helper functions for pattern processing ---


def _process_pattern_group(
    patterns: list[StoredPattern],
    config: StringlyTypedConfig,
    rule_id: str,
    violations: list[Violation],
    covered_variables: set[str],
) -> None:
    """Process a group of patterns with the same hash."""
    if _should_skip_patterns(patterns, config):
        return
    violations.extend(_build_violation(p, patterns, rule_id) for p in patterns)
    for pattern in patterns:
        if pattern.variable_name:
            covered_variables.add(pattern.variable_name)


# --- Helper functions for function call processing ---


def _get_valid_functions(
    storage: StringlyTypedStorage,
    config: StringlyTypedConfig,
) -> list[tuple[str, int, set[str]]]:
    """Get functions that pass all filters."""
    min_files = config.min_occurrences if config.require_cross_file else 1
    limited_funcs = storage.get_limited_value_functions(
        min_values=config.min_values_for_enum,
        max_values=config.max_values_for_enum,
        min_files=min_files,
    )

    return [
        (name, idx, vals)
        for name, idx, vals in limited_funcs
        if not _is_allowed_value_set(vals, config)
        and context_filter.should_include(name, idx, vals)
    ]


def _build_call_violations(
    valid_funcs: list[tuple[str, int, set[str]]],
    storage: StringlyTypedStorage,
) -> list[Violation]:
    """Build violations for valid function patterns."""
    violations: list[Violation] = []
    for function_name, param_index, unique_values in valid_funcs:
        calls = storage.get_calls_by_function(function_name, param_index)
        violations.extend(build_function_call_violations(calls, unique_values))
    return violations


# --- Helper functions for comparison processing ---


def _get_variables_to_check(
    storage: StringlyTypedStorage,
    config: StringlyTypedConfig,
) -> list[tuple[str, set[str]]]:
    """Get variables with multiple values that should be checked."""
    min_files = config.min_occurrences if config.require_cross_file else 1
    return storage.get_variables_with_multiple_values(
        min_values=config.min_values_for_enum,
        min_files=min_files,
    )


def _process_variable(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    variable_name: str,
    unique_values: set[str],
    storage: StringlyTypedStorage,
    config: StringlyTypedConfig,
    covered_variables: set[str],
    violations: list[Violation],
) -> None:
    """Process comparisons for a single variable."""
    if variable_name in covered_variables:
        return
    if _should_skip_variable(variable_name):
        return
    if _should_skip_comparison(unique_values, config):
        return
    comparisons = storage.get_comparisons_by_variable(variable_name)
    violations.extend(
        _build_comparison_violation(c, comparisons, unique_values) for c in comparisons
    )


# --- ViolationGenerator class ---


class ViolationGenerator:
    """Generates violations from cross-file stringly-typed patterns."""

    def __init__(self) -> None:
        """Initialize with helper filters."""
        self._ignore_checker = IgnoreChecker()

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
        pattern_violations, covered_vars = self._generate_pattern_violations(
            storage, rule_id, config
        )
        violations.extend(pattern_violations)
        violations.extend(self._generate_function_call_violations(storage, config))
        violations.extend(self._generate_comparison_violations(storage, config, covered_vars))

        # Apply path-based ignore patterns from config
        violations = _filter_by_ignore(violations, config.ignore)

        # Apply inline ignore directives via IgnoreChecker
        violations = self._ignore_checker.filter_violations(violations)

        return violations

    def _generate_pattern_violations(
        self,
        storage: StringlyTypedStorage,
        rule_id: str,
        config: StringlyTypedConfig,
    ) -> tuple[list[Violation], set[str]]:
        """Generate violations for duplicate validation patterns."""
        duplicate_hashes = storage.get_duplicate_hashes(min_files=config.min_occurrences)
        violations: list[Violation] = []
        covered_variables: set[str] = set()

        for hash_value in duplicate_hashes:
            patterns = storage.get_patterns_by_hash(hash_value)
            _process_pattern_group(patterns, config, rule_id, violations, covered_variables)

        return violations, covered_variables

    def _generate_function_call_violations(
        self,
        storage: StringlyTypedStorage,
        config: StringlyTypedConfig,
    ) -> list[Violation]:
        """Generate violations for function call patterns."""
        valid_funcs = _get_valid_functions(storage, config)
        return _build_call_violations(valid_funcs, storage)

    def _generate_comparison_violations(
        self,
        storage: StringlyTypedStorage,
        config: StringlyTypedConfig,
        covered_variables: set[str] | None = None,
    ) -> list[Violation]:
        """Generate violations for scattered string comparisons."""
        covered_variables = covered_variables or set()
        variables = _get_variables_to_check(storage, config)

        violations: list[Violation] = []
        for variable_name, unique_values in variables:
            _process_variable(
                variable_name, unique_values, storage, config, covered_variables, violations
            )

        return violations

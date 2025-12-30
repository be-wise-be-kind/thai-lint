"""
Purpose: Main stringly-typed linter rule with cross-file detection

Scope: StringlyTypedRule implementing MultiLanguageLintRule for cross-file pattern detection

Overview: Implements stringly-typed linter rule following MultiLanguageLintRule interface with
    cross-file detection using SQLite storage. Orchestrates pattern detection by delegating to
    language-specific analyzers (Python, TypeScript). During check() phase, patterns are collected
    into storage. During finalize() phase, storage is queried for patterns appearing across
    multiple files and violations are generated. Maintains minimal orchestration logic to comply
    with SRP.

Dependencies: MultiLanguageLintRule, BaseLintContext, PythonStringlyTypedAnalyzer,
    StringlyTypedStorage, StorageInitializer, ViolationGenerator, StringlyTypedConfig

Exports: StringlyTypedRule class

Interfaces: StringlyTypedRule.check(context) -> list[Violation],
    StringlyTypedRule.finalize() -> list[Violation]

Implementation: Two-phase pattern: check() stores data, finalize() generates violations.
    Delegates all logic to helper classes, maintains only orchestration and state.

Suppressions:
    - B101: Type narrowing assertions after guards (storage initialized, file_path/content set)
    - srp: Rule class orchestrates cross-file detection with storage, analyzers, and generators.
        Splitting would fragment the two-phase detection workflow.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from src.core.base import BaseLintContext, MultiLanguageLintRule
from src.core.linter_utils import load_linter_config
from src.core.types import Violation

from .config import StringlyTypedConfig
from .ignore_utils import is_ignored
from .python.analyzer import (
    AnalysisResult,
    ComparisonResult,
    FunctionCallResult,
    PythonStringlyTypedAnalyzer,
)
from .storage import StoredComparison, StoredFunctionCall, StoredPattern, StringlyTypedStorage
from .storage_initializer import StorageInitializer
from .typescript.analyzer import TypeScriptStringlyTypedAnalyzer
from .violation_generator import ViolationGenerator


def compute_string_set_hash(values: set[str]) -> int:
    """Compute consistent hash for a set of strings.

    Args:
        values: Set of string values to hash

    Returns:
        Hash value based on sorted, lowercased strings
    """
    return hash(tuple(sorted(s.lower() for s in values)))


def _is_ready_for_analysis(context: BaseLintContext, storage: StringlyTypedStorage | None) -> bool:
    """Check if context and storage are ready for analysis."""
    return bool(context.file_path and context.file_content and storage)


def _convert_to_stored_pattern(result: AnalysisResult) -> StoredPattern:
    """Convert AnalysisResult to StoredPattern.

    Args:
        result: Analysis result from language analyzer

    Returns:
        StoredPattern for storage
    """
    return StoredPattern(
        file_path=result.file_path,
        line_number=result.line_number,
        column=result.column,
        variable_name=result.variable_name,
        string_set_hash=compute_string_set_hash(result.string_values),
        string_values=sorted(result.string_values),
        pattern_type=result.pattern_type,
        details=result.details,
    )


def _convert_to_stored_function_call(result: FunctionCallResult) -> StoredFunctionCall:
    """Convert FunctionCallResult to StoredFunctionCall.

    Args:
        result: Function call result from language analyzer

    Returns:
        StoredFunctionCall for storage
    """
    return StoredFunctionCall(
        file_path=result.file_path,
        line_number=result.line_number,
        column=result.column,
        function_name=result.function_name,
        param_index=result.param_index,
        string_value=result.string_value,
    )


def _convert_to_stored_comparison(result: ComparisonResult) -> StoredComparison:
    """Convert ComparisonResult to StoredComparison.

    Args:
        result: Comparison result from language analyzer

    Returns:
        StoredComparison for storage
    """
    return StoredComparison(
        file_path=result.file_path,
        line_number=result.line_number,
        column=result.column,
        variable_name=result.variable_name,
        compared_value=result.compared_value,
        operator=result.operator,
    )


@dataclass
class StringlyTypedComponents:
    """Component dependencies for stringly-typed linter."""

    storage_initializer: StorageInitializer
    violation_generator: ViolationGenerator
    python_analyzer: PythonStringlyTypedAnalyzer
    typescript_analyzer: TypeScriptStringlyTypedAnalyzer


class StringlyTypedRule(MultiLanguageLintRule):  # thailint: ignore[srp]
    """Detects stringly-typed patterns across project files.

    Uses two-phase pattern:
    1. check() - Collects patterns into SQLite storage (returns empty list)
    2. finalize() - Queries storage and generates violations for cross-file patterns
    """

    def __init__(self) -> None:
        """Initialize the stringly-typed rule with helper components."""
        self._storage: StringlyTypedStorage | None = None
        self._initialized = False
        self._config: StringlyTypedConfig | None = None

        # Helper components grouped to reduce instance attributes
        self._helpers = StringlyTypedComponents(
            storage_initializer=StorageInitializer(),
            violation_generator=ViolationGenerator(),
            python_analyzer=PythonStringlyTypedAnalyzer(),
            typescript_analyzer=TypeScriptStringlyTypedAnalyzer(),
        )

    @property
    def _active_storage(self) -> StringlyTypedStorage:
        """Get storage, asserting it has been initialized.

        Returns:
            The initialized storage instance.

        Raises:
            AssertionError: If storage has not been initialized.
        """
        assert self._storage is not None, "Storage not initialized"  # nosec B101
        return self._storage

    @property
    def rule_id(self) -> str:
        """Unique identifier for this rule."""
        return "stringly-typed.repeated-validation"

    @property
    def rule_name(self) -> str:
        """Human-readable name for this rule."""
        return "Stringly-Typed Pattern"

    @property
    def description(self) -> str:
        """Description of what this rule checks."""
        return "Detects stringly-typed code patterns that should use enums"

    def _load_config(self, context: BaseLintContext) -> StringlyTypedConfig:
        """Load configuration from context.

        Args:
            context: Lint context with metadata

        Returns:
            StringlyTypedConfig instance
        """
        return load_linter_config(context, "stringly_typed", StringlyTypedConfig)

    def _check_python(
        self, context: BaseLintContext, config: StringlyTypedConfig
    ) -> list[Violation]:
        """Analyze Python code and store patterns.

        Args:
            context: Lint context with file content
            config: Stringly-typed configuration

        Returns:
            Empty list (violations generated in finalize)
        """
        self._ensure_storage_initialized(context, config)
        self._analyze_python_file(context, config)
        return []

    def _check_typescript(
        self, context: BaseLintContext, config: StringlyTypedConfig
    ) -> list[Violation]:
        """Analyze TypeScript code and store patterns.

        Args:
            context: Lint context with file content
            config: Stringly-typed configuration

        Returns:
            Empty list (violations generated in finalize)
        """
        self._ensure_storage_initialized(context, config)
        self._analyze_typescript_file(context, config)
        return []

    def _analyze_typescript_file(
        self, context: BaseLintContext, config: StringlyTypedConfig
    ) -> None:
        """Analyze TypeScript file and store patterns.

        Uses single-parse optimization to avoid duplicate parsing overhead.

        Args:
            context: Lint context with file content
            config: Stringly-typed configuration
        """
        if not self._should_analyze(context, config):
            return
        # _should_analyze ensures file_path and file_content are set
        assert context.file_path is not None  # nosec B101
        assert context.file_content is not None  # nosec B101

        self._helpers.typescript_analyzer.config = config
        call_results, comparison_results = self._helpers.typescript_analyzer.analyze_all(
            context.file_content, context.file_path
        )
        self._store_typescript_results(call_results, comparison_results)

    def _store_typescript_results(
        self,
        call_results: list[FunctionCallResult],
        comparison_results: list[ComparisonResult],
    ) -> None:
        """Store TypeScript analysis results.

        Args:
            call_results: Function call patterns found
            comparison_results: Comparison patterns found
        """
        stored_calls = [_convert_to_stored_function_call(r) for r in call_results]
        self._active_storage.add_function_calls(stored_calls)
        stored_comparisons = [_convert_to_stored_comparison(r) for r in comparison_results]
        self._active_storage.add_comparisons(stored_comparisons)

    def _ensure_storage_initialized(
        self, context: BaseLintContext, config: StringlyTypedConfig
    ) -> None:
        """Initialize storage and analyzers on first call.

        Args:
            context: Lint context
            config: Stringly-typed configuration
        """
        if not self._initialized:
            self._storage = self._helpers.storage_initializer.initialize(context, config)
            self._config = config
            self._initialized = True

    def _analyze_python_file(self, context: BaseLintContext, config: StringlyTypedConfig) -> None:
        """Analyze Python file and store patterns.

        Args:
            context: Lint context with file content
            config: Stringly-typed configuration
        """
        if not self._should_analyze(context, config):
            return
        # _should_analyze ensures file_path and file_content are set
        assert context.file_path is not None  # nosec B101
        assert context.file_content is not None  # nosec B101

        file_path = context.file_path
        file_content = context.file_content
        self._helpers.python_analyzer.config = config

        self._store_validation_patterns(file_content, file_path)
        self._store_function_calls(file_content, file_path)
        self._store_comparisons(file_content, file_path)

    def _should_analyze(self, context: BaseLintContext, config: StringlyTypedConfig) -> bool:
        """Check if file should be analyzed.

        Args:
            context: Lint context
            config: Configuration

        Returns:
            True if file should be analyzed
        """
        if not _is_ready_for_analysis(context, self._storage):
            return False
        # _is_ready_for_analysis ensures file_path is set
        assert context.file_path is not None  # nosec B101
        return not is_ignored(context.file_path, config.ignore)

    def _store_validation_patterns(self, file_content: str, file_path: Path) -> None:
        """Analyze and store validation patterns.

        Args:
            file_content: Python source code
            file_path: Path to file
        """
        results = self._helpers.python_analyzer.analyze(file_content, file_path)
        self._active_storage.add_patterns([_convert_to_stored_pattern(r) for r in results])

    def _store_function_calls(self, file_content: str, file_path: Path) -> None:
        """Analyze and store function call patterns.

        Args:
            file_content: Python source code
            file_path: Path to file
        """
        call_results = self._helpers.python_analyzer.analyze_function_calls(file_content, file_path)
        stored_calls = [_convert_to_stored_function_call(r) for r in call_results]
        self._active_storage.add_function_calls(stored_calls)

    def _store_comparisons(self, file_content: str, file_path: Path) -> None:
        """Analyze and store Python comparison patterns.

        Args:
            file_content: Python source code
            file_path: Path to file
        """
        comparison_results = self._helpers.python_analyzer.analyze_comparisons(
            file_content, file_path
        )
        stored_comparisons = [_convert_to_stored_comparison(r) for r in comparison_results]
        self._active_storage.add_comparisons(stored_comparisons)

    def finalize(self) -> list[Violation]:
        """Generate violations after all files processed.

        Returns:
            List of violations for patterns appearing in multiple files
        """
        if not self._storage or not self._config:
            return []

        # Generate violations from cross-file patterns
        violations = self._helpers.violation_generator.generate_violations(
            self._storage, self.rule_id, self._config
        )

        # Cleanup and reset state for next run
        self._storage.close()
        self._storage = None
        self._config = None
        self._initialized = False

        return violations

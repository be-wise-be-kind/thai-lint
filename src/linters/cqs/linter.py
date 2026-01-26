"""
Purpose: Main CQS linter rule implementing MultiLanguageLintRule interface

Scope: Entry point for CQS (Command-Query Separation) violation detection in Python and TypeScript

Overview: Provides CQSRule class that implements the MultiLanguageLintRule interface for
    detecting functions that violate Command-Query Separation by mixing queries (INPUTs)
    with commands (OUTPUTs). Supports both Python (via AST) and TypeScript (via tree-sitter).
    Returns violations for functions that mix operations according to min_operations threshold.
    Supports file path ignore patterns via glob matching.

Dependencies: MultiLanguageLintRule, PythonCQSAnalyzer, TypeScriptCQSAnalyzer, CQSConfig,
    build_cqs_violation

Exports: CQSRule

Interfaces: check(context: BaseLintContext) -> list[Violation]

Implementation: Multi-language analysis with config-driven filtering and min_operations threshold
"""

from fnmatch import fnmatch

from src.core.base import BaseLintContext, MultiLanguageLintRule
from src.core.linter_utils import load_linter_config
from src.core.types import Violation

from .config import CQSConfig
from .python_analyzer import PythonCQSAnalyzer
from .types import CQSPattern
from .typescript_cqs_analyzer import TypeScriptCQSAnalyzer
from .violation_builder import build_cqs_violation


class CQSRule(MultiLanguageLintRule):
    """Detects CQS (Command-Query Separation) violations in Python and TypeScript code."""

    def __init__(self, config: CQSConfig | None = None) -> None:
        """Initialize the CQS rule.

        Args:
            config: Optional configuration override for testing
        """
        super().__init__()
        self._config_override = config
        self._python_analyzer = PythonCQSAnalyzer()
        self._typescript_analyzer = TypeScriptCQSAnalyzer()

    @property
    def rule_id(self) -> str:
        """Unique identifier for this rule."""
        return "cqs"

    @property
    def rule_name(self) -> str:
        """Human-readable name for this rule."""
        return "Command-Query Separation"

    @property
    def description(self) -> str:
        """Description of what this rule checks."""
        return (
            "Detects functions that violate Command-Query Separation by mixing "
            "queries (functions that return values) with commands (functions that "
            "perform side effects). Functions should either query state and return "
            "a value, or command a change without returning data."
        )

    def _load_config(self, context: BaseLintContext) -> CQSConfig:
        """Load configuration from context.

        Args:
            context: Lint context

        Returns:
            CQSConfig object
        """
        if self._config_override is not None:
            return self._config_override
        return load_linter_config(context, "cqs", CQSConfig)

    def _check_python(self, context: BaseLintContext, config: CQSConfig) -> list[Violation]:
        """Check Python code for CQS violations.

        Args:
            context: Lint context with Python file information
            config: Loaded configuration

        Returns:
            List of violations found in Python code
        """
        file_path = str(context.file_path) if context.file_path else "unknown"

        if self._matches_ignore_pattern(file_path, config):
            return []

        patterns = self._python_analyzer.analyze(context.file_content or "", file_path, config)
        return self._patterns_to_violations(patterns, config)

    def _check_typescript(self, context: BaseLintContext, config: CQSConfig) -> list[Violation]:
        """Check TypeScript/JavaScript code for CQS violations.

        Args:
            context: Lint context with TypeScript/JavaScript file information
            config: Loaded configuration

        Returns:
            List of violations found in TypeScript/JavaScript code
        """
        file_path = str(context.file_path) if context.file_path else "unknown"

        if self._matches_ignore_pattern(file_path, config):
            return []

        patterns = self._typescript_analyzer.analyze(context.file_content or "", file_path, config)
        return self._patterns_to_violations(patterns, config)

    def _patterns_to_violations(
        self, patterns: list[CQSPattern], config: CQSConfig
    ) -> list[Violation]:
        """Convert CQSPatterns to Violations, applying thresholds.

        Args:
            patterns: List of CQSPattern objects
            config: CQS configuration

        Returns:
            List of Violation objects
        """
        violating_patterns = [p for p in patterns if self._is_violation(p, config)]
        return [build_cqs_violation(p) for p in violating_patterns]

    def _matches_ignore_pattern(self, file_path: str, config: CQSConfig) -> bool:
        """Check if file path matches any ignore pattern.

        Args:
            file_path: Path to check
            config: CQS configuration

        Returns:
            True if path matches an ignore pattern
        """
        return any(fnmatch(file_path, pattern) for pattern in config.ignore_patterns)

    def _is_violation(self, pattern: CQSPattern, config: CQSConfig) -> bool:
        """Check if pattern represents a violation based on config.

        Args:
            pattern: CQSPattern to check
            config: CQS configuration

        Returns:
            True if pattern is a violation
        """
        if not pattern.has_violation():
            return False

        min_ops = config.min_operations
        return len(pattern.inputs) >= min_ops and len(pattern.outputs) >= min_ops

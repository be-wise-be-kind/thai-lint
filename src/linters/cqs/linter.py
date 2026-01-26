"""
Purpose: Main CQS linter rule implementing PythonOnlyLintRule interface

Scope: Entry point for CQS (Command-Query Separation) violation detection in Python code

Overview: Provides CQSRule class that implements the PythonOnlyLintRule interface for
    detecting functions that violate Command-Query Separation by mixing queries (INPUTs)
    with commands (OUTPUTs). Returns violations for functions that mix operations according
    to min_operations threshold. Supports file path ignore patterns via glob matching.

Dependencies: PythonOnlyLintRule, PythonCQSAnalyzer, CQSConfig, build_cqs_violation

Exports: CQSRule

Interfaces: check(context: BaseLintContext) -> list[Violation]

Implementation: Single-file analysis with config-driven filtering and min_operations threshold
"""

from fnmatch import fnmatch

from src.core.python_lint_rule import PythonOnlyLintRule
from src.core.types import Violation

from .config import CQSConfig
from .python_analyzer import PythonCQSAnalyzer
from .types import CQSPattern
from .violation_builder import build_cqs_violation


class CQSRule(PythonOnlyLintRule[CQSConfig]):
    """Detects CQS (Command-Query Separation) violations in Python code."""

    def __init__(self, config: CQSConfig | None = None) -> None:
        """Initialize the CQS rule."""
        super().__init__(config)
        self._analyzer = PythonCQSAnalyzer()

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

    @property
    def _config_key(self) -> str:
        """Configuration key in metadata."""
        return "cqs"

    @property
    def _config_class(self) -> type[CQSConfig]:
        """Configuration class type."""
        return CQSConfig

    def _analyze(self, code: str, file_path: str, config: CQSConfig) -> list[Violation]:
        """Analyze code for CQS violations."""
        if self._matches_ignore_pattern(file_path, config):
            return []

        patterns = self._analyzer.analyze(code, file_path, config)
        violating_patterns = [p for p in patterns if self._is_violation(p, config)]
        return [build_cqs_violation(p) for p in violating_patterns]

    def _matches_ignore_pattern(self, file_path: str, config: CQSConfig) -> bool:
        """Check if file path matches any ignore pattern."""
        return any(fnmatch(file_path, pattern) for pattern in config.ignore_patterns)

    def _is_violation(self, pattern: CQSPattern, config: CQSConfig) -> bool:
        """Check if pattern represents a violation based on config."""
        if not pattern.has_violation():
            return False

        min_ops = config.min_operations
        return len(pattern.inputs) >= min_ops and len(pattern.outputs) >= min_ops

"""
Purpose: Main LBYL linter rule implementing PythonOnlyLintRule interface

Scope: Entry point for LBYL anti-pattern detection in Python code

Overview: Provides LBYLRule class that implements the PythonOnlyLintRule interface for
    detecting Look Before You Leap anti-patterns in Python code. Validates that files
    are Python with content, loads configuration, and delegates analysis to
    PythonLBYLAnalyzer. Returns violations with EAFP suggestions for detected patterns.
    Supports disabling via configuration and pattern-specific toggles.

Dependencies: PythonOnlyLintRule, PythonLBYLAnalyzer, LBYLConfig

Exports: LBYLRule

Interfaces: check(context: BaseLintContext) -> list[Violation]

Implementation: Single-file analysis with config-driven pattern detection
"""

from src.core.python_lint_rule import PythonOnlyLintRule
from src.core.types import Violation

from .config import LBYLConfig
from .python_analyzer import PythonLBYLAnalyzer


class LBYLRule(PythonOnlyLintRule[LBYLConfig]):
    """Detects Look Before You Leap anti-patterns in Python code."""

    def __init__(self, config: LBYLConfig | None = None) -> None:
        """Initialize the LBYL rule."""
        super().__init__(config)
        self._analyzer = PythonLBYLAnalyzer()

    @property
    def rule_id(self) -> str:
        """Unique identifier for this rule."""
        return "lbyl"

    @property
    def rule_name(self) -> str:
        """Human-readable name for this rule."""
        return "Look Before You Leap"

    @property
    def description(self) -> str:
        """Description of what this rule checks."""
        return (
            "Detects LBYL (Look Before You Leap) anti-patterns that should be "
            "refactored to EAFP (Easier to Ask Forgiveness than Permission) style "
            "using try/except blocks."
        )

    @property
    def _config_key(self) -> str:
        """Configuration key in metadata."""
        return "lbyl"

    @property
    def _config_class(self) -> type[LBYLConfig]:
        """Configuration class type."""
        return LBYLConfig

    def _analyze(self, code: str, file_path: str, config: LBYLConfig) -> list[Violation]:
        """Analyze code for LBYL violations."""
        return self._analyzer.analyze(code, file_path, config)

"""
Purpose: Main LBYL linter rule implementing BaseLintRule interface

Scope: Entry point for LBYL anti-pattern detection in Python code

Overview: Provides LBYLRule class that implements the BaseLintRule interface for
    detecting Look Before You Leap anti-patterns in Python code. Validates that
    files are Python with content, loads configuration via load_linter_config,
    and delegates analysis to PythonLBYLAnalyzer. Returns violations with EAFP
    suggestions for detected patterns. Supports disabling via configuration and
    pattern-specific toggles.

Dependencies: BaseLintRule, load_linter_config, PythonLBYLAnalyzer, LBYLConfig

Exports: LBYLRule

Interfaces: check(context: BaseLintContext) -> list[Violation]

Implementation: Single-file analysis with config-driven pattern detection
"""

from src.core.base import BaseLintContext, BaseLintRule
from src.core.constants import Language
from src.core.linter_utils import has_file_content, load_linter_config
from src.core.types import Violation

from .config import LBYLConfig
from .python_analyzer import PythonLBYLAnalyzer


class LBYLRule(BaseLintRule):
    """Detects Look Before You Leap anti-patterns in Python code."""

    def __init__(self, config: LBYLConfig | None = None) -> None:
        """Initialize the LBYL rule.

        Args:
            config: Optional configuration override for testing
        """
        self._config_override = config
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

    def check(self, context: BaseLintContext) -> list[Violation]:
        """Check for LBYL violations in the given context.

        Args:
            context: The lint context containing file information.

        Returns:
            List of violations for detected LBYL patterns.
        """
        if not self._should_analyze(context):
            return []

        config = self._get_config(context)
        if not config.enabled:
            return []

        file_path = str(context.file_path) if context.file_path else "unknown"
        return self._analyzer.analyze(context.file_content or "", file_path, config)

    def _should_analyze(self, context: BaseLintContext) -> bool:
        """Check if context should be analyzed."""
        return context.language == Language.PYTHON and has_file_content(context)

    def _get_config(self, context: BaseLintContext) -> LBYLConfig:
        """Get configuration, using override if provided."""
        if self._config_override is not None:
            return self._config_override
        return load_linter_config(context, "lbyl", LBYLConfig)

"""
Purpose: Main stateless class linter rule implementation

Scope: StatelessClassRule class implementing BaseLintRule interface

Overview: Implements stateless class linter rule following BaseLintRule interface.
    Detects Python classes that have no constructor (__init__ or __new__), no instance
    state (self.attr assignments), and 2+ methods - indicating they should be refactored
    to module-level functions. Delegates AST analysis to StatelessClassAnalyzer.

Dependencies: BaseLintRule, BaseLintContext, Violation, StatelessClassAnalyzer

Exports: StatelessClassRule class

Interfaces: StatelessClassRule.check(context) -> list[Violation]

Implementation: Composition pattern delegating analysis to specialized analyzer
"""

from src.core.base import BaseLintContext, BaseLintRule
from src.core.types import Severity, Violation

from .python_analyzer import ClassInfo, StatelessClassAnalyzer


class StatelessClassRule(BaseLintRule):
    """Detects stateless classes that should be module-level functions."""

    def __init__(self) -> None:
        """Initialize the rule with analyzer."""
        self._analyzer = StatelessClassAnalyzer()

    @property
    def rule_id(self) -> str:
        """Unique identifier for this rule."""
        return "stateless-class.violation"

    @property
    def rule_name(self) -> str:
        """Human-readable name for this rule."""
        return "Stateless Class Detection"

    @property
    def description(self) -> str:
        """Description of what this rule checks."""
        return "Classes without state should be refactored to module-level functions"

    def check(self, context: BaseLintContext) -> list[Violation]:
        """Check for stateless class violations.

        Args:
            context: Lint context with file information

        Returns:
            List of violations found
        """
        if not self._should_analyze(context):
            return []

        stateless_classes = self._analyzer.analyze(context.file_content)  # type: ignore
        return [self._create_violation(info, context) for info in stateless_classes]

    def _should_analyze(self, context: BaseLintContext) -> bool:
        """Check if context should be analyzed.

        Args:
            context: Lint context

        Returns:
            True if should analyze
        """
        return context.language == "python" and context.file_content is not None

    def _create_violation(self, info: ClassInfo, context: BaseLintContext) -> Violation:
        """Create violation from class info.

        Args:
            info: Detected stateless class info
            context: Lint context

        Returns:
            Violation instance
        """
        message = (
            f"Class '{info.name}' has no state and should be refactored to module-level functions"
        )
        return Violation(
            rule_id=self.rule_id,
            message=message,
            file_path=str(context.file_path),
            line=info.line,
            column=info.column,
            severity=Severity.ERROR,
        )

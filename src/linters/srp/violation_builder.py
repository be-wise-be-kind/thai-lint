"""
Purpose: Violation creation with suggestions for SRP linter

Scope: Builds Violation objects with contextual messages and refactoring suggestions

Overview: Provides violation building functionality for the SRP linter. Creates violations
    from class metrics and issue descriptions, generates contextual error messages, and
    provides actionable refactoring suggestions based on issue types (methods, lines, keywords).
    Isolates violation construction and suggestion generation from metrics evaluation and
    class analysis to maintain single responsibility.

Dependencies: BaseLintContext, Violation, Severity, typing, src.core.violation_builder

Exports: ViolationBuilder

Interfaces: build_violation(metrics, issues, rule_id, context) -> Violation

Implementation: Formats messages from metrics, generates targeted suggestions per issue type,
    extends BaseViolationBuilder for consistent violation construction
"""

from typing import Any

from src.core.base import BaseLintContext
from src.core.types import Severity, Violation
from src.core.violation_builder import BaseViolationBuilder, ViolationInfo


class ViolationBuilder(BaseViolationBuilder):
    """Builds SRP violations with messages and suggestions."""

    def __init__(self) -> None:  # pylint: disable=useless-parent-delegation
        """Initialize the violation builder."""
        super().__init__()  # Inherits from BaseViolationBuilder

    def build_violation(
        self,
        metrics: dict[str, Any],
        issues: list[str],
        rule_id: str,
        context: BaseLintContext,
    ) -> Violation:
        """Build violation from metrics and issues.

        Args:
            metrics: Class metrics dictionary
            issues: List of issue descriptions
            rule_id: Rule identifier
            context: Lint context

        Returns:
            Violation with message and suggestion
        """
        message = f"Class '{metrics['class_name']}' may violate SRP: {', '.join(issues)}"
        suggestion = self._generate_suggestion(issues)

        info = ViolationInfo(
            rule_id=rule_id,
            file_path=str(context.file_path or ""),
            line=metrics["line"],
            column=metrics["column"],
            message=message,
            severity=Severity.ERROR,
            suggestion=suggestion,
        )
        return self.build(info)

    def _generate_suggestion(self, issues: list[str]) -> str:
        """Generate refactoring suggestion based on issues.

        Args:
            issues: List of issue descriptions

        Returns:
            Suggestion string with refactoring advice
        """
        suggestions = [
            self._suggest_for_methods(issues),
            self._suggest_for_lines(issues),
            self._suggest_for_keywords(issues),
        ]
        return ". ".join(filter(None, suggestions))

    def _suggest_for_methods(self, issues: list[str]) -> str:
        """Suggest fix for too many methods.

        Args:
            issues: List of issue descriptions

        Returns:
            Suggestion string or empty string
        """
        if any("methods" in issue for issue in issues):
            return "Consider extracting related methods into separate classes"
        return ""

    def _suggest_for_lines(self, issues: list[str]) -> str:
        """Suggest fix for too many lines.

        Args:
            issues: List of issue descriptions

        Returns:
            Suggestion string or empty string
        """
        if any("lines" in issue for issue in issues):
            return "Consider breaking the class into smaller, focused classes"
        return ""

    def _suggest_for_keywords(self, issues: list[str]) -> str:
        """Suggest fix for responsibility keywords.

        Args:
            issues: List of issue descriptions

        Returns:
            Suggestion string or empty string
        """
        if any("keyword" in issue for issue in issues):
            return "Avoid generic names like Manager, Handler, Processor"
        return ""

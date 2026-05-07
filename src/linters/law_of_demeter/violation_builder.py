"""
Purpose: Violation creation for Law of Demeter linter

Scope: Builds Violation objects for LoD chain depth violations

Overview: Provides violation building functionality for the Law of Demeter linter. Creates
    violations for Python code with excessive chain depth, generates contextual error messages
    including chain representation and depth, and provides actionable refactoring suggestions.
    Handles syntax errors gracefully. Extends BaseViolationBuilder for consistent violation
    construction across all linters.

Dependencies: ast, src.core.base, src.core.types, src.core.violation_builder

Exports: DemeterViolationBuilder

Interfaces: create_chain_violation, create_syntax_error_violation

Implementation: Formats messages with chain depth information, provides refactoring suggestions
"""

import ast
from typing import Any

from src.core.base import BaseLintContext
from src.core.types import Severity, Violation
from src.core.violation_builder import BaseViolationBuilder


class DemeterViolationBuilder(BaseViolationBuilder):
    """Builds violations for Law of Demeter chain depth issues."""

    def __init__(self, rule_id: str):
        """Initialize violation builder.

        Args:
            rule_id: Rule identifier for violations
        """
        super().__init__()
        self.rule_id = rule_id

    def create_chain_violation(
        self,
        node: ast.AST,
        parts: list[str],
        context: BaseLintContext,
    ) -> Violation:
        """Create violation for excessive chain depth.

        Args:
            node: AST node where chain was found
            parts: Chain parts list
            context: Lint context

        Returns:
            Chain depth violation
        """
        depth = len(parts) - 1
        chain_str = ".".join(parts)
        lineno = getattr(node, "lineno", 0)
        col = getattr(node, "col_offset", 0)

        return self.build_from_params(
            rule_id=self.rule_id,
            file_path=str(context.file_path or ""),
            line=lineno,
            column=col,
            message=_format_message(chain_str, depth),
            severity=Severity.ERROR,
            suggestion=_format_suggestion(depth),
        )

    def create_syntax_error_violation(self, error: SyntaxError, context: Any) -> Violation:
        """Create violation for syntax error.

        Args:
            error: SyntaxError exception
            context: Lint context

        Returns:
            Syntax error violation
        """
        return self.build_from_params(
            rule_id=self.rule_id,
            file_path=str(context.file_path or ""),
            line=error.lineno or 0,
            column=error.offset or 0,
            message=f"Syntax error: {error.msg}",
            severity=Severity.ERROR,
            suggestion="Fix syntax errors before checking chain depth",
        )


def _format_message(chain_str: str, depth: int) -> str:
    """Format violation message with chain and depth info."""
    return f"Law of Demeter violation: chain depth {depth} in '{chain_str}'"


def _format_suggestion(depth: int) -> str:
    """Format refactoring suggestion based on chain depth."""
    return (
        f"Chain depth of {depth} exceeds limit. "
        "Consider introducing a local variable, "
        "using a wrapper method, or applying the 'Tell, Don't Ask' principle "
        "to reduce coupling between objects."
    )

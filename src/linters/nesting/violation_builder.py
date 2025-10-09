"""
Purpose: Violation creation for nesting depth linter

Scope: Builds Violation objects for nesting depth violations

Overview: Provides violation building functionality for the nesting depth linter. Creates
    violations for Python and TypeScript functions with excessive nesting, generates contextual
    error messages with actual vs maximum depth, and provides actionable refactoring suggestions
    (early returns, guard clauses, extract method). Handles syntax errors gracefully. Isolates
    violation construction from analysis and checking logic.

Dependencies: ast, BaseLintContext, Violation, Severity, NestingConfig, src.core.violation_builder

Exports: NestingViolationBuilder

Interfaces: create_nesting_violation, create_typescript_nesting_violation, create_syntax_error_violation

Implementation: Formats messages with depth information, provides targeted refactoring suggestions,
    extends BaseViolationBuilder for consistent violation construction
"""

import ast
from typing import Any

from src.core.base import BaseLintContext
from src.core.types import Severity, Violation
from src.core.violation_builder import BaseViolationBuilder

from .config import NestingConfig


class NestingViolationBuilder(BaseViolationBuilder):
    """Builds violations for nesting depth issues."""

    def __init__(self, rule_id: str):
        """Initialize violation builder.

        Args:
            rule_id: Rule identifier for violations
        """
        self.rule_id = rule_id

    def create_syntax_error_violation(
        self, error: SyntaxError, context: BaseLintContext
    ) -> Violation:
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
            suggestion="Fix syntax errors before checking nesting depth",
        )

    def create_nesting_violation(
        self,
        func: ast.FunctionDef | ast.AsyncFunctionDef,
        max_depth: int,
        config: NestingConfig,
        context: BaseLintContext,
    ) -> Violation:
        """Create violation for excessive nesting in Python function.

        Args:
            func: Python function AST node
            max_depth: Actual max nesting depth found
            config: Nesting configuration
            context: Lint context

        Returns:
            Nesting depth violation
        """
        return self.build_from_params(
            rule_id=self.rule_id,
            file_path=str(context.file_path or ""),
            line=func.lineno,
            column=func.col_offset,
            message=f"Function '{func.name}' has excessive nesting depth ({max_depth})",
            severity=Severity.ERROR,
            suggestion=self._generate_suggestion(max_depth, config.max_nesting_depth),
        )

    def create_typescript_nesting_violation(
        self,
        func_info: tuple[Any, str],
        max_depth: int,
        config: NestingConfig,
        context: BaseLintContext,
    ) -> Violation:
        """Create violation for excessive nesting in TypeScript function.

        Args:
            func_info: Tuple of (func_node, func_name)
            max_depth: Actual max nesting depth found
            config: Nesting configuration
            context: Lint context

        Returns:
            Nesting depth violation
        """
        func_node, func_name = func_info
        line = func_node.start_point[0] + 1  # Convert to 1-indexed
        column = func_node.start_point[1]

        return self.build_from_params(
            rule_id=self.rule_id,
            file_path=str(context.file_path or ""),
            line=line,
            column=column,
            message=f"Function '{func_name}' has excessive nesting depth ({max_depth})",
            severity=Severity.ERROR,
            suggestion=self._generate_suggestion(max_depth, config.max_nesting_depth),
        )

    def _generate_suggestion(self, actual_depth: int, max_depth: int) -> str:
        """Generate refactoring suggestion based on depth.

        Args:
            actual_depth: Actual nesting depth found
            max_depth: Maximum allowed depth

        Returns:
            Suggestion string with refactoring advice
        """
        return (
            f"Maximum nesting depth of {actual_depth} exceeds limit of {max_depth}. "
            "Consider extracting nested logic to separate functions, using early returns, "
            "or applying guard clauses to reduce nesting."
        )

"""
File: src/linters/print_statements/violation_builder.py

Purpose: Builds Violation objects for print statement detection

Exports: ViolationBuilder class

Depends: ast, pathlib.Path, src.core.types.Violation

Implements: ViolationBuilder.create_python_violation(node, line, file_path) -> Violation,
    ViolationBuilder.create_typescript_violation(method, line, file_path) -> Violation

Related: src/linters/magic_numbers/violation_builder.py, src/core/types.py

Overview: Provides ViolationBuilder class that creates Violation objects for print statement
    detections. Generates descriptive messages suggesting the use of proper logging instead of
    print/console statements. Constructs complete Violation instances with rule_id, file_path,
    line number, column, message, and suggestions. Provides separate methods for Python print()
    violations and TypeScript/JavaScript console.* violations with language-appropriate messages.

Usage: builder = ViolationBuilder("print-statements.detected")
    violation = builder.create_python_violation(node, line, file_path)

Notes: Message templates suggest logging as alternative, consistent with other linter patterns
"""

import ast
from pathlib import Path

from src.core.types import Violation


class ViolationBuilder:
    """Builds violations for print statement detections."""

    def __init__(self, rule_id: str) -> None:
        """Initialize the violation builder.

        Args:
            rule_id: The rule ID to use in violations
        """
        self.rule_id = rule_id

    def create_python_violation(
        self,
        node: ast.Call,
        line: int,
        file_path: Path | None,
    ) -> Violation:
        """Create a violation for a Python print() call.

        Args:
            node: The AST Call node containing the print statement
            line: Line number where the violation occurs
            file_path: Path to the file

        Returns:
            Violation object with details about the print statement
        """
        message = "print() statement should be replaced with proper logging"
        suggestion = "Use logging.info(), logging.debug(), or similar instead of print()"

        return Violation(
            rule_id=self.rule_id,
            file_path=str(file_path) if file_path else "",
            line=line,
            column=node.col_offset if hasattr(node, "col_offset") else 0,
            message=message,
            suggestion=suggestion,
        )

    def create_typescript_violation(
        self,
        method: str,
        line: int,
        file_path: Path | None,
    ) -> Violation:
        """Create a violation for a TypeScript/JavaScript console.* call.

        Args:
            method: The console method name (log, warn, error, etc.)
            line: Line number where the violation occurs
            file_path: Path to the file

        Returns:
            Violation object with details about the console statement
        """
        message = f"console.{method}() should be replaced with proper logging"
        suggestion = f"Use a logging library instead of console.{method}()"

        return Violation(
            rule_id=self.rule_id,
            file_path=str(file_path) if file_path else "",
            line=line,
            column=0,  # Tree-sitter nodes don't provide easy column access
            message=message,
            suggestion=suggestion,
        )

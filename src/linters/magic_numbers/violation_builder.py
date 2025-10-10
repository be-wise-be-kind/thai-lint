"""
Purpose: Builds Violation objects for magic number detection

Scope: Violation message construction for magic numbers linter

Overview: Provides ViolationBuilder class that creates Violation objects for magic number detections.
    Generates helpful, descriptive messages suggesting constant extraction for numeric literals.
    Constructs complete Violation instances with rule_id, file_path, line number, column, message,
    and suggestions. Formats messages to mention the specific numeric value and encourage using
    named constants for better code maintainability and readability. Provides consistent violation
    structure across all magic number detections.

Dependencies: src.core.types for Violation dataclass, pathlib for Path handling, ast for node types

Exports: ViolationBuilder class

Interfaces: ViolationBuilder.create_violation(node, value, line, file_path) -> Violation,
    builds complete Violation object with all required fields

Implementation: Message template with value interpolation, structured violation construction
"""

import ast
from pathlib import Path

from src.core.types import Violation


class ViolationBuilder:
    """Builds violations for magic number detections."""

    def __init__(self, rule_id: str) -> None:
        """Initialize the violation builder.

        Args:
            rule_id: The rule ID to use in violations
        """
        self.rule_id = rule_id

    def create_violation(
        self,
        node: ast.Constant,
        value: int | float,
        line: int,
        file_path: Path | None,
    ) -> Violation:
        """Create a violation for a magic number.

        Args:
            node: The AST node containing the magic number
            value: The numeric value
            line: Line number where the violation occurs
            file_path: Path to the file

        Returns:
            Violation object with details about the magic number
        """
        message = f"Magic number {value} should be a named constant"

        suggestion = f"Extract {value} to a named constant (e.g., CONSTANT_NAME = {value})"

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
        value: int | float,
        line: int,
        file_path: Path | None,
    ) -> Violation:
        """Create a violation for a TypeScript magic number.

        Args:
            value: The numeric value
            line: Line number where the violation occurs
            file_path: Path to the file

        Returns:
            Violation object with details about the magic number
        """
        message = f"Magic number {value} should be a named constant"

        suggestion = f"Extract {value} to a named constant (e.g., const CONSTANT_NAME = {value})"

        return Violation(
            rule_id=self.rule_id,
            file_path=str(file_path) if file_path else "",
            line=line,
            column=0,  # Tree-sitter nodes don't have easy column access
            message=message,
            suggestion=suggestion,
        )

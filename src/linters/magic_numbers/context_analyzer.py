"""
Purpose: Analyzes contexts to determine if numeric literals are acceptable

Scope: Context detection for magic number acceptable usage patterns

Overview: Provides ContextAnalyzer class that determines whether a numeric literal is in an acceptable
    context where it should not be flagged as a magic number. Detects acceptable contexts including
    constant definitions (UPPERCASE names), small integers in range() or enumerate() calls, test files,
    and configuration contexts. Uses AST node analysis to inspect parent nodes and determine the usage
    pattern of numeric literals. Helps reduce false positives by distinguishing between legitimate
    numeric literals and true magic numbers that should be extracted to constants. Method count (10)
    exceeds SRP limit (8) because refactoring for A-grade complexity requires extracting helper methods.
    Class maintains single responsibility of context analysis - all methods support this core purpose.

Dependencies: ast module for AST node types, pathlib for Path handling

Exports: ContextAnalyzer class

Interfaces: ContextAnalyzer.is_acceptable_context(node, parent, file_path, config) -> bool,
    various helper methods for specific context checks

Implementation: AST parent node inspection, pattern matching for acceptable contexts, configurable
    max_small_integer threshold for range detection
"""

import ast
from pathlib import Path


class ContextAnalyzer:  # thailint: ignore[srp]
    """Analyzes contexts to determine if numeric literals are acceptable."""

    def __init__(self) -> None:
        """Initialize the context analyzer."""
        pass  # Stateless analyzer for context checking

    def is_acceptable_context(
        self,
        node: ast.Constant,
        parent: ast.AST | None,
        file_path: Path | None,
        config: dict,
    ) -> bool:
        """Check if a numeric literal is in an acceptable context.

        Args:
            node: The numeric constant node
            parent: The parent node in the AST
            file_path: Path to the file being analyzed
            config: Configuration with allowed_numbers and max_small_integer

        Returns:
            True if the context is acceptable and should not be flagged
        """
        # File-level and definition checks
        if self.is_test_file(file_path) or self.is_constant_definition(node, parent):
            return True

        # Usage pattern checks
        return self._is_acceptable_usage_pattern(node, parent, config)

    def _is_acceptable_usage_pattern(
        self, node: ast.Constant, parent: ast.AST | None, config: dict
    ) -> bool:
        """Check if numeric literal is in acceptable usage pattern.

        Args:
            node: The numeric constant node
            parent: The parent node in the AST
            config: Configuration with max_small_integer threshold

        Returns:
            True if usage pattern is acceptable
        """
        if self.is_small_integer_in_range(node, parent, config):
            return True

        if self.is_small_integer_in_enumerate(node, parent, config):
            return True

        return self.is_string_repetition(node, parent)

    def is_test_file(self, file_path: Path | None) -> bool:
        """Check if the file is a test file.

        Args:
            file_path: Path to the file

        Returns:
            True if the file is a test file (matches test_*.py pattern)
        """
        if not file_path:
            return False
        return file_path.name.startswith("test_") or "_test.py" in file_path.name

    def is_constant_definition(self, node: ast.Constant, parent: ast.AST | None) -> bool:
        """Check if the number is part of an UPPERCASE constant definition.

        Args:
            node: The numeric constant node
            parent: The parent node in the AST

        Returns:
            True if this is a constant definition
        """
        if not self._is_assignment_node(parent):
            return False

        # Type narrowing: parent is ast.Assign after the check above
        assert isinstance(parent, ast.Assign)  # nosec B101
        return self._has_constant_target(parent)

    def _is_assignment_node(self, parent: ast.AST | None) -> bool:
        """Check if parent is an assignment node."""
        return parent is not None and isinstance(parent, ast.Assign)

    def _has_constant_target(self, parent: ast.Assign) -> bool:
        """Check if assignment has uppercase constant target."""
        return any(
            isinstance(target, ast.Name) and self._is_constant_name(target.id)
            for target in parent.targets
        )

    def _is_constant_name(self, name: str) -> bool:
        """Check if a name follows constant naming convention.

        Args:
            name: Variable name to check

        Returns:
            True if the name is UPPERCASE (constant convention)
        """
        return name.isupper() and len(name) > 1

    def is_small_integer_in_range(
        self, node: ast.Constant, parent: ast.AST | None, config: dict
    ) -> bool:
        """Check if this is a small integer used in range() call.

        Args:
            node: The numeric constant node
            parent: The parent node in the AST
            config: Configuration with max_small_integer threshold

        Returns:
            True if this is a small integer in range()
        """
        if not isinstance(node.value, int):
            return False

        max_small_int = config.get("max_small_integer", 10)
        if not 0 <= node.value <= max_small_int:
            return False

        return self._is_in_range_call(parent)

    def is_small_integer_in_enumerate(
        self, node: ast.Constant, parent: ast.AST | None, config: dict
    ) -> bool:
        """Check if this is a small integer used in enumerate() call.

        Args:
            node: The numeric constant node
            parent: The parent node in the AST
            config: Configuration with max_small_integer threshold

        Returns:
            True if this is a small integer in enumerate()
        """
        if not isinstance(node.value, int):
            return False

        max_small_int = config.get("max_small_integer", 10)
        if not 0 <= node.value <= max_small_int:
            return False

        return self._is_in_enumerate_call(parent)

    def _is_in_range_call(self, parent: ast.AST | None) -> bool:
        """Check if the parent is a range() call.

        Args:
            parent: The parent node

        Returns:
            True if parent is range() call
        """
        return (
            isinstance(parent, ast.Call)
            and isinstance(parent.func, ast.Name)
            and parent.func.id == "range"
        )

    def _is_in_enumerate_call(self, parent: ast.AST | None) -> bool:
        """Check if the parent is an enumerate() call.

        Args:
            parent: The parent node

        Returns:
            True if parent is enumerate() call
        """
        return (
            isinstance(parent, ast.Call)
            and isinstance(parent.func, ast.Name)
            and parent.func.id == "enumerate"
        )

    def is_string_repetition(self, node: ast.Constant, parent: ast.AST | None) -> bool:
        """Check if this number is used in string repetition (e.g., "-" * 40).

        Args:
            node: The numeric constant node
            parent: The parent node in the AST

        Returns:
            True if this is a string repetition pattern
        """
        if not isinstance(node.value, int):
            return False

        if not isinstance(parent, ast.BinOp):
            return False

        if not isinstance(parent.op, ast.Mult):
            return False

        # Check if either operand is a string constant
        return self._has_string_operand(parent)

    def _has_string_operand(self, binop: ast.BinOp) -> bool:
        """Check if binary operation has a string operand.

        Args:
            binop: Binary operation node

        Returns:
            True if either left or right operand is a string constant
        """
        return self._is_string_constant(binop.left) or self._is_string_constant(binop.right)

    def _is_string_constant(self, node: ast.AST) -> bool:
        """Check if a node is a string constant.

        Args:
            node: AST node to check

        Returns:
            True if node is a Constant with string value
        """
        return isinstance(node, ast.Constant) and isinstance(node.value, str)

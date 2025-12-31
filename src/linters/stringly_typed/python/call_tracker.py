"""
Purpose: Detect function calls with string literal arguments in Python AST

Scope: Find function and method calls that consistently receive string arguments

Overview: Provides FunctionCallTracker class that traverses Python AST to find function
    and method calls where string literals are passed as arguments. Tracks the function
    name, parameter index, and string value to enable cross-file aggregation. When a
    function is called with the same set of limited string values across files, it
    suggests the parameter should be an enum. Handles both simple function calls
    (foo("value")) and method calls (obj.method("value")).

Dependencies: ast module for AST parsing, dataclasses for pattern structure,
    src.core.constants for MAX_ATTRIBUTE_CHAIN_DEPTH

Exports: FunctionCallTracker class, FunctionCallPattern dataclass

Interfaces: FunctionCallTracker.find_patterns(tree) -> list[FunctionCallPattern]

Implementation: AST NodeVisitor pattern with Call node handling for string arguments

Suppressions:
    - invalid-name: visit_Call follows AST NodeVisitor method naming convention
"""

import ast
from dataclasses import dataclass

from src.core.constants import MAX_ATTRIBUTE_CHAIN_DEPTH


@dataclass
class FunctionCallPattern:
    """Represents a function call with a string literal argument.

    Captures information about a function or method call where a string literal
    is passed as an argument, enabling cross-file analysis to detect limited
    value sets that should be enums.
    """

    function_name: str
    """Fully qualified function name (e.g., 'process' or 'obj.method')."""

    param_index: int
    """Index of the parameter receiving the string value (0-indexed)."""

    string_value: str
    """The string literal value passed to the function."""

    line_number: int
    """Line number where the call occurs (1-indexed)."""

    column: int
    """Column number where the call starts (0-indexed)."""


class FunctionCallTracker(ast.NodeVisitor):
    """Tracks function calls with string literal arguments.

    Finds patterns like 'process("active")' and 'obj.set_status("pending")' where
    string literals are used for arguments that could be enums.
    """

    def __init__(self) -> None:
        """Initialize the tracker."""
        self.patterns: list[FunctionCallPattern] = []

    def find_patterns(self, tree: ast.AST) -> list[FunctionCallPattern]:
        """Find all function calls with string arguments in the AST.

        Args:
            tree: The AST to analyze

        Returns:
            List of FunctionCallPattern instances for each detected call
        """
        self.patterns = []
        self.visit(tree)
        return self.patterns

    def visit_Call(self, node: ast.Call) -> None:  # pylint: disable=invalid-name
        """Visit a Call node to check for string arguments.

        Handles both simple function calls and method calls, extracting
        the function name and any string literal arguments.

        Args:
            node: The Call node to analyze
        """
        function_name = self._extract_function_name(node.func)
        if function_name is None:
            self.generic_visit(node)
            return

        self._check_positional_args(node, function_name)
        self.generic_visit(node)

    def _extract_function_name(self, func_node: ast.expr) -> str | None:
        """Extract the function name from a call expression.

        Handles simple names (foo) and attribute access (obj.method).

        Args:
            func_node: The function expression node

        Returns:
            Function name string or None if not extractable
        """
        if isinstance(func_node, ast.Name):
            return func_node.id
        if isinstance(func_node, ast.Attribute):
            return self._extract_attribute_name(func_node)
        return None

    def _extract_attribute_name(self, node: ast.Attribute) -> str | None:
        """Extract function name from an attribute access.

        Builds qualified names like 'obj.method' or 'a.b.method'.

        Args:
            node: The Attribute node

        Returns:
            Qualified function name or None if too complex
        """
        parts: list[str] = [node.attr]
        current = node.value
        depth = 0

        while depth < MAX_ATTRIBUTE_CHAIN_DEPTH:
            if isinstance(current, ast.Name):
                parts.append(current.id)
                break
            if isinstance(current, ast.Attribute):
                parts.append(current.attr)
                current = current.value
                depth += 1
            else:
                # Complex expression (call result, subscript, etc.)
                # Use placeholder to maintain function identity
                parts.append("_")
                break

        return ".".join(reversed(parts))

    def _check_positional_args(self, node: ast.Call, function_name: str) -> None:
        """Check positional arguments for string literals.

        Args:
            node: The Call node
            function_name: Extracted function name
        """
        for param_index, arg in enumerate(node.args):
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                self._add_pattern(node, function_name, param_index, arg.value)

    def _add_pattern(
        self, node: ast.Call, function_name: str, param_index: int, string_value: str
    ) -> None:
        """Create and add a function call pattern to results.

        Args:
            node: The Call node containing the pattern
            function_name: Name of the function being called
            param_index: Index of the string argument
            string_value: The string literal value
        """
        pattern = FunctionCallPattern(
            function_name=function_name,
            param_index=param_index,
            string_value=string_value,
            line_number=node.lineno,
            column=node.col_offset,
        )
        self.patterns.append(pattern)

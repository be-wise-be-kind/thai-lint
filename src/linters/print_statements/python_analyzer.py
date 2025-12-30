"""
Purpose: Python AST analysis for finding print() call nodes

Scope: Python print() statement detection and __main__ block context analysis

Overview: Provides PythonPrintStatementAnalyzer class that traverses Python AST to find all
    print() function calls. Uses ast.walk() to traverse the syntax tree and collect
    Call nodes where the function is 'print'. Tracks parent nodes to detect if print calls
    are within __main__ blocks (if __name__ == "__main__":) for allow_in_scripts filtering.
    Returns structured data about each print call including the AST node, parent context,
    and line number for violation reporting. Handles both simple print() and builtins.print() calls.

Dependencies: ast module for AST parsing and node types, analyzers.ast_utils

Exports: PythonPrintStatementAnalyzer class, is_print_call function, is_main_if_block function

Interfaces: find_print_calls(tree) -> list[tuple[Call, AST | None, int]], is_in_main_block(node) -> bool

Implementation: AST walk pattern with parent map for context detection and __main__ block identification
"""

import ast

from src.analyzers.ast_utils import build_parent_map

# --- Pure helper functions for print call detection ---


def is_print_call(node: ast.Call) -> bool:
    """Check if a Call node is calling print().

    Args:
        node: The Call node to check

    Returns:
        True if this is a print() call
    """
    return _is_simple_print(node) or _is_builtins_print(node)


def _is_simple_print(node: ast.Call) -> bool:
    """Check for simple print() call."""
    return isinstance(node.func, ast.Name) and node.func.id == "print"


def _is_builtins_print(node: ast.Call) -> bool:
    """Check for builtins.print() call."""
    if not isinstance(node.func, ast.Attribute):
        return False
    if node.func.attr != "print":
        return False
    return isinstance(node.func.value, ast.Name) and node.func.value.id == "builtins"


# --- Pure helper functions for __main__ block detection ---


def is_main_if_block(node: ast.AST) -> bool:
    """Check if node is an `if __name__ == "__main__":` statement.

    Args:
        node: AST node to check

    Returns:
        True if this is a __main__ if block
    """
    if not isinstance(node, ast.If):
        return False
    if not isinstance(node.test, ast.Compare):
        return False
    return _is_main_comparison(node.test)


def _is_main_comparison(test: ast.Compare) -> bool:
    """Check if comparison is __name__ == '__main__'."""
    if not _is_name_identifier(test.left):
        return False
    if not _has_single_eq_operator(test):
        return False
    return _compares_to_main(test)


def _is_name_identifier(node: ast.expr) -> bool:
    """Check if node is the __name__ identifier."""
    return isinstance(node, ast.Name) and node.id == "__name__"


def _has_single_eq_operator(test: ast.Compare) -> bool:
    """Check if comparison has single == operator."""
    return len(test.ops) == 1 and isinstance(test.ops[0], ast.Eq)


def _compares_to_main(test: ast.Compare) -> bool:
    """Check if comparison is to '__main__' string."""
    if len(test.comparators) != 1:
        return False
    comparator = test.comparators[0]
    return isinstance(comparator, ast.Constant) and comparator.value == "__main__"


# --- Analyzer class with stateful parent tracking ---


class PythonPrintStatementAnalyzer:
    """Analyzes Python AST to find print() calls."""

    def __init__(self) -> None:
        """Initialize the analyzer."""
        self.print_calls: list[tuple[ast.Call, ast.AST | None, int]] = []
        self.parent_map: dict[ast.AST, ast.AST] = {}

    def find_print_calls(self, tree: ast.AST) -> list[tuple[ast.Call, ast.AST | None, int]]:
        """Find all print() calls in the AST.

        Args:
            tree: The AST to analyze

        Returns:
            List of tuples (node, parent, line_number)
        """
        self.print_calls = []
        self.parent_map = build_parent_map(tree)
        self._collect_print_calls(tree)
        return self.print_calls

    def _collect_print_calls(self, tree: ast.AST) -> None:
        """Walk tree and collect all print() calls.

        Args:
            tree: AST to traverse
        """
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and is_print_call(node):
                parent = self.parent_map.get(node)
                line_number = node.lineno if hasattr(node, "lineno") else 0
                self.print_calls.append((node, parent, line_number))

    def is_in_main_block(self, node: ast.AST) -> bool:
        """Check if node is within `if __name__ == "__main__":` block.

        Args:
            node: AST node to check

        Returns:
            True if node is inside a __main__ block
        """
        current = node
        while current in self.parent_map:
            parent = self.parent_map[current]
            if is_main_if_block(parent):
                return True
            current = parent
        return False

"""
Purpose: Python AST analysis for finding print() call nodes

Scope: Python print() statement detection and __main__ block context analysis

Overview: Provides PythonPrintStatementAnalyzer class that traverses Python AST to find all
    print() function calls. Uses ast.walk() to traverse the syntax tree and collect
    Call nodes where the function is 'print'. Tracks parent nodes to detect if print calls
    are within __main__ blocks (if __name__ == "__main__":) for allow_in_scripts filtering.
    Returns structured data about each print call including the AST node, parent context,
    and line number for violation reporting. Handles both simple print() and builtins.print() calls.

Dependencies: ast module for AST parsing and node types

Exports: PythonPrintStatementAnalyzer class

Interfaces: find_print_calls(tree) -> list[tuple[Call, AST | None, int]], is_in_main_block(node) -> bool

Implementation: AST walk pattern with parent map for context detection and __main__ block identification
"""

import ast


class PythonPrintStatementAnalyzer:  # thailint: ignore[srp]
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
        self.parent_map = {}
        self._build_parent_map(tree)
        self._collect_print_calls(tree)
        return self.print_calls

    def _build_parent_map(self, node: ast.AST, parent: ast.AST | None = None) -> None:
        """Build a map of nodes to their parents.

        Args:
            node: Current AST node
            parent: Parent of current node
        """
        if parent is not None:
            self.parent_map[node] = parent

        for child in ast.iter_child_nodes(node):
            self._build_parent_map(child, node)

    def _collect_print_calls(self, tree: ast.AST) -> None:
        """Walk tree and collect all print() calls.

        Args:
            tree: AST to traverse
        """
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and self._is_print_call(node):
                parent = self.parent_map.get(node)
                line_number = node.lineno if hasattr(node, "lineno") else 0
                self.print_calls.append((node, parent, line_number))

    def _is_print_call(self, node: ast.Call) -> bool:
        """Check if a Call node is calling print().

        Args:
            node: The Call node to check

        Returns:
            True if this is a print() call
        """
        return self._is_simple_print(node) or self._is_builtins_print(node)

    def _is_simple_print(self, node: ast.Call) -> bool:
        """Check for simple print() call."""
        return isinstance(node.func, ast.Name) and node.func.id == "print"

    def _is_builtins_print(self, node: ast.Call) -> bool:
        """Check for builtins.print() call."""
        if not isinstance(node.func, ast.Attribute):
            return False
        if node.func.attr != "print":
            return False
        return isinstance(node.func.value, ast.Name) and node.func.value.id == "builtins"

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
            if self._is_main_if_block(parent):
                return True
            current = parent
        return False

    def _is_main_if_block(self, node: ast.AST) -> bool:
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
        return self._is_main_comparison(node.test)

    def _is_main_comparison(self, test: ast.Compare) -> bool:
        """Check if comparison is __name__ == '__main__'."""
        if not self._is_name_identifier(test.left):
            return False
        if not self._has_single_eq_operator(test):
            return False
        return self._compares_to_main(test)

    def _is_name_identifier(self, node: ast.expr) -> bool:
        """Check if node is the __name__ identifier."""
        return isinstance(node, ast.Name) and node.id == "__name__"

    def _has_single_eq_operator(self, test: ast.Compare) -> bool:
        """Check if comparison has single == operator."""
        return len(test.ops) == 1 and isinstance(test.ops[0], ast.Eq)

    def _compares_to_main(self, test: ast.Compare) -> bool:
        """Check if comparison is to '__main__' string."""
        if len(test.comparators) != 1:
            return False
        comparator = test.comparators[0]
        return isinstance(comparator, ast.Constant) and comparator.value == "__main__"

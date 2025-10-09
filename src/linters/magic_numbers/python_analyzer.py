"""
Purpose: Python AST analysis for finding numeric literal nodes

Scope: Python magic number detection through AST traversal

Overview: Provides PythonMagicNumberAnalyzer class that traverses Python AST to find all numeric
    literal nodes (integers and floats). Uses ast.NodeVisitor pattern to walk the syntax tree and
    collect Constant nodes containing numeric values along with their parent nodes and line numbers.
    Returns structured data about each numeric literal including the AST node, parent node, numeric
    value, and source location. This analyzer handles Python-specific AST structure and provides
    the foundation for magic number detection by identifying all candidates before context filtering.

Dependencies: ast module for AST parsing and node types

Exports: PythonMagicNumberAnalyzer class

Interfaces: PythonMagicNumberAnalyzer.find_numeric_literals(tree) -> list[tuple],
    returns list of (node, parent, value, line_number) tuples

Implementation: AST NodeVisitor pattern with parent tracking, filters for numeric Constant nodes
"""

import ast
from typing import Any


class PythonMagicNumberAnalyzer(ast.NodeVisitor):
    """Analyzes Python AST to find numeric literals."""

    def __init__(self) -> None:
        """Initialize the analyzer."""
        self.numeric_literals: list[tuple[ast.Constant, ast.AST | None, Any, int]] = []
        self.parent_map: dict[ast.AST, ast.AST] = {}

    def find_numeric_literals(
        self, tree: ast.AST
    ) -> list[tuple[ast.Constant, ast.AST | None, Any, int]]:
        """Find all numeric literals in the AST.

        Args:
            tree: The AST to analyze

        Returns:
            List of tuples (node, parent, value, line_number)
        """
        self.numeric_literals = []
        self.parent_map = {}
        self._build_parent_map(tree)
        self.visit(tree)
        return self.numeric_literals

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

    def visit_Constant(self, node: ast.Constant) -> None:
        """Visit a Constant node and check if it's a numeric literal.

        Args:
            node: The Constant node to check
        """
        if isinstance(node.value, (int, float)):
            parent = self.parent_map.get(node)
            line_number = node.lineno if hasattr(node, "lineno") else 0
            self.numeric_literals.append((node, parent, node.value, line_number))

        self.generic_visit(node)

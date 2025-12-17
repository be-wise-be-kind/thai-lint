"""
Purpose: Python AST-based nesting depth calculator

Scope: Python code nesting depth analysis using ast module

Overview: Analyzes Python code to calculate maximum nesting depth using AST traversal. Implements
    visitor pattern to walk AST, tracking current depth and maximum depth found. Increments depth
    for If, For, While, With, AsyncWith, Try, ExceptHandler, Match, and match_case nodes. Starts
    depth counting at 1 for function body, matching reference implementation behavior. Returns
    maximum depth found and location information for violation reporting. Provides helper method
    to find all function definitions in an AST tree for batch processing.

Dependencies: ast module for Python parsing

Exports: PythonNestingAnalyzer class with calculate_max_depth method

Interfaces: calculate_max_depth(func_node: ast.FunctionDef) -> tuple[int, int], find_all_functions

Implementation: AST visitor pattern with depth tracking, based on reference implementation algorithm
"""

import ast


class PythonNestingAnalyzer:
    """Calculates maximum nesting depth in Python functions."""

    def __init__(self) -> None:
        """Initialize the Python nesting analyzer."""
        pass  # Stateless analyzer for nesting depth calculation

    def calculate_max_depth(
        self, func_node: ast.FunctionDef | ast.AsyncFunctionDef
    ) -> tuple[int, int]:
        """Calculate maximum nesting depth in a function.

        Args:
            func_node: AST node for function definition

        Returns:
            Tuple of (max_depth, line_number_of_max_depth)
        """
        max_depth = 0
        max_depth_line = func_node.lineno

        def visit_node(node: ast.AST, current_depth: int = 0) -> None:
            nonlocal max_depth, max_depth_line

            if current_depth > max_depth:
                max_depth = current_depth
                max_depth_line = getattr(node, "lineno", func_node.lineno)

            # Nodes that increase nesting depth
            if isinstance(
                node,
                (
                    ast.If,
                    ast.For,
                    ast.While,
                    ast.With,
                    ast.AsyncWith,
                    ast.Try,
                    ast.ExceptHandler,
                    ast.Match,
                    ast.match_case,
                ),
            ):
                current_depth += 1

            # Visit children
            for child in ast.iter_child_nodes(node):
                visit_node(child, current_depth)

        # Start at depth 1 for function body (matching reference implementation)
        for stmt in func_node.body:
            visit_node(stmt, 1)

        return max_depth, max_depth_line

    def find_all_functions(self, tree: ast.AST) -> list[ast.FunctionDef | ast.AsyncFunctionDef]:
        """Find all function definitions in AST.

        Args:
            tree: Python AST to search

        Returns:
            List of all FunctionDef and AsyncFunctionDef nodes found
        """
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                functions.append(node)
        return functions

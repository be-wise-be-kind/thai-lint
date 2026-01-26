"""
Purpose: Python AST-based nesting depth calculator

Scope: Python code nesting depth analysis using ast module

Overview: Analyzes Python code to calculate maximum nesting depth using AST traversal. Implements
    visitor pattern to walk AST, tracking current depth and maximum depth found. Increments depth
    for If, For, While, With, AsyncWith, Try, ExceptHandler, Match, and match_case nodes. Correctly
    handles elif chains by detecting when an If node is in elif position (sole child in parent's
    orelse list) and not incrementing depth. Starts depth counting at 1 for function body, matching
    reference implementation behavior. Returns maximum depth found and location information for
    violation reporting. Provides helper method to find all function definitions in an AST tree
    for batch processing.

Dependencies: ast module for Python parsing

Exports: PythonNestingAnalyzer class with calculate_max_depth method

Interfaces: calculate_max_depth(func_node: ast.FunctionDef) -> tuple[int, int], find_all_functions

Implementation: AST visitor pattern with depth tracking, elif detection via parent orelse inspection
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

        def _record_depth(node: ast.AST, depth: int) -> None:
            """Record max depth if this depth is the highest seen."""
            nonlocal max_depth, max_depth_line
            if depth > max_depth:
                max_depth = depth
                max_depth_line = getattr(node, "lineno", func_node.lineno)

        def visit_node(node: ast.AST, current_depth: int = 0, is_elif: bool = False) -> None:
            """Visit AST node, tracking nesting depth for control structures only."""
            # Only record max depth when entering a control structure
            # Skip depth increment for If nodes in elif position
            if isinstance(node, ast.If):
                if not is_elif:
                    current_depth += 1
                    _record_depth(node, current_depth)
                _visit_if_children(node, current_depth)
            elif isinstance(
                node,
                (
                    ast.For,
                    ast.While,
                    ast.With,
                    ast.AsyncWith,
                    ast.Try,
                    ast.Match,
                    ast.match_case,
                ),
            ):
                current_depth += 1
                _record_depth(node, current_depth)
                for child in ast.iter_child_nodes(node):
                    visit_node(child, current_depth, is_elif=False)
            else:
                # Non-control-structure nodes: just visit children, no depth recording
                for child in ast.iter_child_nodes(node):
                    visit_node(child, current_depth, is_elif=False)

        def _visit_if_children(node: ast.If, current_depth: int) -> None:
            """Visit If node children with special handling for elif chains."""
            # Visit body normally
            for child in node.body:
                visit_node(child, current_depth, is_elif=False)

            # Check if orelse is an elif (single If node in orelse)
            if _is_elif_chain(node.orelse):
                visit_node(node.orelse[0], current_depth, is_elif=True)
            else:
                # Regular else block - visit all children normally
                for child in node.orelse:
                    visit_node(child, current_depth, is_elif=False)

        # Start at depth 0 - control structures increment when entered
        for stmt in func_node.body:
            visit_node(stmt, 0)

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


def _is_elif_chain(orelse: list[ast.stmt]) -> bool:
    """Check if orelse list represents an elif (single If node).

    Args:
        orelse: The orelse list from an If node

    Returns:
        True if this is an elif (single If in orelse), False otherwise
    """
    return len(orelse) == 1 and isinstance(orelse[0], ast.If)

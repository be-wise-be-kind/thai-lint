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


# Control structure types that increase nesting depth
_CONTROL_STRUCTURES = (
    ast.For,
    ast.While,
    ast.With,
    ast.AsyncWith,
    ast.Try,
    ast.Match,
    ast.match_case,
)


class _DepthTracker:
    """Tracks maximum nesting depth during AST traversal."""

    def __init__(self, default_line: int) -> None:
        """Initialize tracker with default line number."""
        self.max_depth = 0
        self.max_depth_line = default_line

    def record(self, node: ast.AST, depth: int, default_line: int) -> None:
        """Record depth if it's the new maximum."""
        if depth > self.max_depth:
            self.max_depth = depth
            self.max_depth_line = getattr(node, "lineno", default_line)


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
        tracker = _DepthTracker(func_node.lineno)

        for stmt in func_node.body:
            _visit_node(stmt, 0, tracker, func_node.lineno)

        return tracker.max_depth, tracker.max_depth_line

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


def _visit_node(
    node: ast.AST, current_depth: int, tracker: _DepthTracker, default_line: int, is_elif: bool = False
) -> None:
    """Visit AST node, tracking nesting depth for control structures only."""
    if isinstance(node, ast.If):
        _visit_if_node(node, current_depth, tracker, default_line, is_elif)
    elif isinstance(node, _CONTROL_STRUCTURES):
        _visit_control_structure(node, current_depth, tracker, default_line)
    else:
        _visit_children(node, current_depth, tracker, default_line)


def _visit_if_node(
    node: ast.If, current_depth: int, tracker: _DepthTracker, default_line: int, is_elif: bool
) -> None:
    """Visit If node with special elif handling."""
    if not is_elif:
        current_depth += 1
        tracker.record(node, current_depth, default_line)

    # Visit body
    for child in node.body:
        _visit_node(child, current_depth, tracker, default_line)

    # Handle orelse - check for elif chain
    if _is_elif_chain(node.orelse):
        _visit_node(node.orelse[0], current_depth, tracker, default_line, is_elif=True)
    else:
        for child in node.orelse:
            _visit_node(child, current_depth, tracker, default_line)


def _visit_control_structure(
    node: ast.AST, current_depth: int, tracker: _DepthTracker, default_line: int
) -> None:
    """Visit a control structure node that increases depth."""
    current_depth += 1
    tracker.record(node, current_depth, default_line)
    _visit_children(node, current_depth, tracker, default_line)


def _visit_children(
    node: ast.AST, current_depth: int, tracker: _DepthTracker, default_line: int
) -> None:
    """Visit all children of a node without incrementing depth."""
    for child in ast.iter_child_nodes(node):
        _visit_node(child, current_depth, tracker, default_line)


def _is_elif_chain(orelse: list[ast.stmt]) -> bool:
    """Check if orelse list represents an elif (single If node).

    Args:
        orelse: The orelse list from an If node

    Returns:
        True if this is an elif (single If in orelse), False otherwise
    """
    return len(orelse) == 1 and isinstance(orelse[0], ast.If)

"""
Purpose: Rust AST-based nesting depth calculator

Scope: Rust code nesting depth analysis using tree-sitter parser

Overview: Analyzes Rust code to calculate maximum nesting depth using AST traversal.
    Extends RustBaseAnalyzer to reuse common tree-sitter initialization and parsing.
    Implements visitor pattern to walk Rust AST, tracking current depth and maximum
    depth found. Increments depth for control flow statements (if, match, loop, while,
    for) and closures. Returns maximum depth and location for each function.

Dependencies: RustBaseAnalyzer, TREE_SITTER_RUST_AVAILABLE

Exports: RustNestingAnalyzer class with calculate_max_depth and find_all_functions

Interfaces: calculate_max_depth(func_node) -> tuple[int, int], find_all_functions(root_node)

Implementation: Inherits tree-sitter parsing from base, visitor pattern with depth tracking
"""

from typing import Any

from src.analyzers.rust_base import TREE_SITTER_RUST_AVAILABLE, RustBaseAnalyzer


class RustNestingAnalyzer(RustBaseAnalyzer):
    """Calculates maximum nesting depth in Rust functions."""

    # Tree-sitter node types that increase nesting depth
    NESTING_NODE_TYPES = {
        "if_expression",
        "match_expression",
        "loop_expression",
        "while_expression",
        "for_expression",
        "closure_expression",
    }

    def calculate_max_depth(self, func_node: Any) -> tuple[int, int]:
        """Calculate maximum nesting depth in a Rust function.

        Args:
            func_node: Function item AST node

        Returns:
            Tuple of (max_depth, line_number)
        """
        if not TREE_SITTER_RUST_AVAILABLE:
            return 0, 0

        body_node = self._find_function_body(func_node)
        if not body_node:
            return 0, func_node.start_point[0] + 1

        max_depth = 0
        max_depth_line = body_node.start_point[0] + 1

        def visit_node(node: Any, current_depth: int = 0) -> None:
            nonlocal max_depth, max_depth_line

            if current_depth > max_depth:
                max_depth = current_depth
                max_depth_line = node.start_point[0] + 1

            new_depth = current_depth + 1 if node.type in self.NESTING_NODE_TYPES else current_depth

            for child in node.children:
                visit_node(child, new_depth)

        # Start at depth 1 for function body children
        for child in body_node.children:
            visit_node(child, 1)

        return max_depth, max_depth_line

    def find_all_functions(self, root_node: Any) -> list[tuple[Any, str]]:
        """Find all function definitions in Rust AST.

        Args:
            root_node: Root node to search from

        Returns:
            List of (function_node, function_name) tuples
        """
        if not TREE_SITTER_RUST_AVAILABLE or root_node is None:
            return []

        functions: list[tuple[Any, str]] = []
        self._collect_functions_recursive(root_node, functions)
        return functions

    def _collect_functions_recursive(self, node: Any, functions: list[tuple[Any, str]]) -> None:
        """Recursively collect function nodes from Rust AST.

        Args:
            node: Current node to examine
            functions: List to append found functions to
        """
        if node.type == "function_item":
            name = self.extract_identifier_name(node)
            functions.append((node, name))

        for child in node.children:
            self._collect_functions_recursive(child, functions)

    def _find_function_body(self, func_node: Any) -> Any:
        """Find the block node (function body) in a function item.

        Args:
            func_node: Function item node to search

        Returns:
            Block node or None
        """
        for child in func_node.children:
            if child.type == "block":
                return child
        return None

"""
Purpose: TypeScript AST-based nesting depth calculator

Scope: TypeScript code nesting depth analysis using tree-sitter parser

Overview: Analyzes TypeScript code to calculate maximum nesting depth using AST traversal.
    Extends TypeScriptBaseAnalyzer to reuse common tree-sitter initialization and parsing.
    Delegates function extraction to TypeScriptFunctionExtractor. Implements visitor pattern
    to walk TypeScript AST, tracking current depth and maximum depth found. Increments depth
    for control flow statements. Returns maximum depth and location.

Dependencies: TypeScriptBaseAnalyzer, TypeScriptFunctionExtractor

Exports: TypeScriptNestingAnalyzer class with calculate_max_depth methods

Interfaces: calculate_max_depth(func_node) -> tuple[int, int], find_all_functions(root_node)

Implementation: Inherits tree-sitter parsing from base, visitor pattern with depth tracking
"""

from typing import Any

from src.analyzers.typescript_base import TypeScriptBaseAnalyzer

# dry: ignore-block - tree-sitter import pattern (common across TypeScript analyzers)
try:
    from tree_sitter import Node

    TREE_SITTER_AVAILABLE = True
except ImportError:
    TREE_SITTER_AVAILABLE = False
    Node = Any  # type: ignore

from .typescript_function_extractor import TypeScriptFunctionExtractor


class TypeScriptNestingAnalyzer(TypeScriptBaseAnalyzer):
    """Calculates maximum nesting depth in TypeScript functions."""

    # Tree-sitter node types that increase nesting depth
    NESTING_NODE_TYPES = {
        "if_statement",
        "for_statement",
        "for_in_statement",
        "while_statement",
        "do_statement",
        "try_statement",
        "switch_statement",
        "with_statement",  # Deprecated but exists
    }

    def __init__(self) -> None:
        """Initialize analyzer with function extractor."""
        super().__init__()
        self.function_extractor = TypeScriptFunctionExtractor()

    def calculate_max_depth(self, func_node: Node) -> tuple[int, int]:
        """Calculate maximum nesting depth in a TypeScript function.

        Args:
            func_node: Function AST node

        Returns:
            Tuple of (max_depth, line_number)
        """
        if not TREE_SITTER_AVAILABLE:
            return 0, 0

        body_node = self._find_function_body(func_node)
        if not body_node:
            return 0, func_node.start_point[0] + 1

        max_depth = 0
        max_depth_line = body_node.start_point[0] + 1

        def visit_node(node: Node, current_depth: int = 0) -> None:
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

    def find_all_functions(self, root_node: Node) -> list[tuple[Node, str]]:
        """Find all function definitions in TypeScript AST.

        Args:
            root_node: Root node to search from

        Returns:
            List of (function_node, function_name) tuples
        """
        return self.function_extractor.collect_all_functions(root_node)

    def _find_function_body(self, func_node: Node) -> Node | None:
        """Find the statement_block node in a function.

        Args:
            func_node: Function node to search

        Returns:
            Statement block node or None
        """
        for child in func_node.children:
            if child.type == "statement_block":
                return child
        return None

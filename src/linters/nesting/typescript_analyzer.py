"""
Purpose: TypeScript AST-based nesting depth calculator

Scope: TypeScript code nesting depth analysis using tree-sitter parser

Overview: Analyzes TypeScript code to calculate maximum nesting depth using AST traversal with
    tree-sitter parser. Delegates function extraction to TypeScriptFunctionExtractor. Implements
    visitor pattern to walk TypeScript AST, tracking current depth and maximum depth found.
    Increments depth for control flow statements. Returns maximum depth and location.

Dependencies: tree-sitter, tree-sitter-typescript, TypeScriptFunctionExtractor

Exports: TypeScriptNestingAnalyzer class with calculate_max_depth and parse_typescript methods

Interfaces: calculate_max_depth(func_node) -> tuple[int, int], parse_typescript(code: str)

Implementation: tree-sitter AST visitor pattern with depth tracking, composition with extractor
"""

from typing import Any

try:
    import tree_sitter_typescript as tstypescript
    from tree_sitter import Language, Node, Parser

    TS_LANGUAGE = Language(tstypescript.language_typescript())
    TS_PARSER = Parser(TS_LANGUAGE)
    TREE_SITTER_AVAILABLE = True
except ImportError:
    TREE_SITTER_AVAILABLE = False
    TS_PARSER = None  # type: ignore
    Node = Any  # type: ignore

from .typescript_function_extractor import TypeScriptFunctionExtractor


class TypeScriptNestingAnalyzer:
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

    def __init__(self):
        """Initialize analyzer with function extractor."""
        self.function_extractor = TypeScriptFunctionExtractor()

    def parse_typescript(self, code: str) -> Node | None:
        """Parse TypeScript code to AST using tree-sitter.

        Args:
            code: TypeScript source code to parse

        Returns:
            Tree-sitter AST root node, or None if parsing fails
        """
        if not TREE_SITTER_AVAILABLE or TS_PARSER is None:
            return None

        tree = TS_PARSER.parse(bytes(code, "utf8"))
        return tree.root_node

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

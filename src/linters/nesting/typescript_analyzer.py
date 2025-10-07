"""
Purpose: TypeScript AST-based nesting depth calculator

Scope: TypeScript code nesting depth analysis using tree-sitter parser

Overview: Analyzes TypeScript code to calculate maximum nesting depth using AST traversal.
    Implements visitor pattern to walk TypeScript AST from tree-sitter, tracking current depth
    and maximum depth found. Increments depth for if_statement, for_statement, for_in_statement,
    while_statement, do_statement, try_statement, switch_statement nodes. Starts depth counting
    at 1 for function body. Returns maximum depth found and location.

Dependencies: tree-sitter, tree-sitter-typescript for TypeScript parsing

Exports: TypeScriptNestingAnalyzer class with calculate_max_depth and parse_typescript methods

Interfaces: calculate_max_depth(func_node) -> tuple[int, int], parse_typescript(code: str)

Implementation: tree-sitter AST visitor pattern with depth tracking for TypeScript
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
        """Calculate maximum nesting depth in a TypeScript function."""
        if not TREE_SITTER_AVAILABLE:
            return 0, 0

        body_node = self._find_function_body(func_node)
        if not body_node:
            return 0, func_node.start_point[0] + 1

        return self._calculate_depth_in_body(body_node)

    def _find_function_body(self, func_node: Node) -> Node | None:
        """Find the statement_block node in a function."""
        for child in func_node.children:
            if child.type == "statement_block":
                return child
        return None

    def _calculate_depth_in_body(self, body_node: Node) -> tuple[int, int]:
        """Calculate max depth within a function body."""
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

        for child in body_node.children:
            visit_node(child, 1)

        return max_depth, max_depth_line

    def find_all_functions(self, root_node: Node) -> list[tuple[Node, str]]:
        """Find all function definitions in TypeScript AST.

        Args:
            root_node: Tree-sitter root node

        Returns:
            List of tuples: (function_node, function_name)
        """
        if not TREE_SITTER_AVAILABLE:
            return []

        functions: list[tuple[Node, str]] = []
        self._collect_functions(root_node, functions)
        return functions

    def _collect_functions(self, node: Node, functions: list[tuple[Node, str]]) -> None:
        """Recursively collect function nodes from AST."""
        function_entry = self._extract_function_if_applicable(node)
        if function_entry:
            functions.append(function_entry)

        for child in node.children:
            self._collect_functions(child, functions)

    def _extract_function_if_applicable(self, node: Node) -> tuple[Node, str] | None:
        """Extract function node and name if node is a function type."""
        if node.type == "function_declaration":
            return self._extract_function_declaration(node)
        if node.type == "arrow_function":
            return self._extract_arrow_function(node)
        if node.type == "method_definition":
            return self._extract_method_definition(node)
        if node.type in ("function_expression", "function"):
            return self._extract_function_expression(node)
        return None

    def _extract_function_declaration(self, node: Node) -> tuple[Node, str]:
        """Extract name from function declaration node."""
        name_node = self._find_child_by_type(node, "identifier")
        name = name_node.text.decode("utf8") if name_node and name_node.text else "<anonymous>"
        return (node, name)

    def _extract_arrow_function(self, node: Node) -> tuple[Node, str]:
        """Extract name from arrow function node."""
        name = "<arrow>"
        parent = node.parent
        if parent and parent.type == "variable_declarator":
            id_node = self._find_child_by_type(parent, "identifier")
            if id_node and id_node.text:
                name = id_node.text.decode("utf8")
        return (node, name)

    def _extract_method_definition(self, node: Node) -> tuple[Node, str]:
        """Extract name from method definition node."""
        name_node = self._find_child_by_type(node, "property_identifier")
        name = name_node.text.decode("utf8") if name_node and name_node.text else "<method>"
        return (node, name)

    def _extract_function_expression(self, node: Node) -> tuple[Node, str]:
        """Extract name from function expression node."""
        name = "<function>"
        parent = node.parent
        if parent and parent.type == "variable_declarator":
            id_node = self._find_child_by_type(parent, "identifier")
            if id_node and id_node.text:
                name = id_node.text.decode("utf8")
        return (node, name)

    def _find_child_by_type(self, node: Node, child_type: str) -> Node | None:
        """Find first child node matching the given type."""
        for child in node.children:
            if child.type == child_type:
                return child
        return None

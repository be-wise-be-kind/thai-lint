"""
Purpose: Base class for TypeScript AST analysis with tree-sitter parsing

Scope: Common tree-sitter initialization, parsing, and traversal utilities for TypeScript

Overview: Provides shared infrastructure for TypeScript code analysis using tree-sitter parser.
    Implements common tree-sitter initialization with language setup and parser configuration.
    Provides reusable parsing methods that convert TypeScript source to AST nodes. Includes
    shared traversal utilities for walking AST trees recursively and finding nodes by type.
    Centralizes node extraction patterns including name extraction from identifiers and
    type identifiers. Serves as foundation for specialized analyzers (SRP, nesting, DRY)
    to eliminate duplicate tree-sitter boilerplate.

Dependencies: tree-sitter, tree-sitter-typescript

Exports: TypeScriptBaseAnalyzer class with parsing and traversal utilities

Interfaces: parse_typescript(code), walk_tree(node, node_type), extract_node_text(node)

Implementation: Tree-sitter parser singleton, recursive AST traversal, composition pattern
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
    TS_PARSER = None  # type: ignore[assignment]
    Node = Any  # type: ignore[assignment,misc]


class TypeScriptBaseAnalyzer:
    """Base analyzer for TypeScript code using tree-sitter."""

    def __init__(self) -> None:
        """Initialize TypeScript base analyzer."""
        self.tree_sitter_available = TREE_SITTER_AVAILABLE

    def parse_typescript(self, code: str) -> Node | None:
        """Parse TypeScript code to AST using tree-sitter.

        Args:
            code: TypeScript source code to parse

        Returns:
            Tree-sitter AST root node, or None if parsing fails or tree-sitter unavailable
        """
        if not TREE_SITTER_AVAILABLE or TS_PARSER is None:
            return None

        tree = TS_PARSER.parse(bytes(code, "utf8"))
        return tree.root_node

    def walk_tree(self, node: Node, node_type: str) -> list[Node]:
        """Find all nodes of a specific type in the AST.

        Recursively walks the tree and collects all nodes matching the given type.

        Args:
            node: Root tree-sitter node to search from
            node_type: Tree-sitter node type to find (e.g., "class_declaration")

        Returns:
            List of all matching nodes
        """
        if not TREE_SITTER_AVAILABLE or node is None:
            return []

        nodes: list[Node] = []
        self._walk_tree_recursive(node, node_type, nodes)
        return nodes

    def _walk_tree_recursive(self, node: Node, node_type: str, nodes: list[Node]) -> None:
        """Recursively walk tree to find nodes of specific type.

        Args:
            node: Current tree-sitter node
            node_type: Node type to find
            nodes: List to accumulate matching nodes
        """
        if node.type == node_type:
            nodes.append(node)

        for child in node.children:
            self._walk_tree_recursive(child, node_type, nodes)

    def extract_node_text(self, node: Node) -> str:
        """Extract text content from a tree-sitter node.

        Args:
            node: Tree-sitter node

        Returns:
            Decoded text content of the node
        """
        text = node.text
        if text is None:
            return ""
        return text.decode()

    def find_child_by_type(self, node: Node, child_type: str) -> Node | None:
        """Find first child node of a specific type.

        Args:
            node: Parent node to search
            child_type: Child node type to find

        Returns:
            First matching child node or None
        """
        for child in node.children:
            if child.type == child_type:
                return child
        return None

    def find_children_by_types(self, node: Node, child_types: set[str]) -> list[Node]:
        """Find all children matching any of the given types.

        Args:
            node: Parent node to search
            child_types: Set of child node types to find

        Returns:
            List of matching child nodes
        """
        return [child for child in node.children if child.type in child_types]

    def extract_identifier_name(self, node: Node) -> str:
        """Extract identifier or type_identifier name from node children.

        Common pattern for extracting names from class/function declarations.

        Args:
            node: Node to extract identifier from

        Returns:
            Identifier name or default fallback
        """
        for child in node.children:
            if child.type in ("identifier", "type_identifier", "property_identifier"):
                return self.extract_node_text(child)
        return "anonymous"

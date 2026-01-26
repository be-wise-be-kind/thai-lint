"""
Purpose: Base class for Rust AST analysis with tree-sitter parsing

Scope: Common tree-sitter initialization, parsing, and traversal utilities for Rust

Overview: Provides shared infrastructure for Rust code analysis using tree-sitter parser.
    Implements common tree-sitter initialization with language setup and parser configuration.
    Provides reusable parsing methods that convert Rust source to AST nodes. Includes
    shared traversal utilities for walking AST trees recursively and finding nodes by type.
    Delegates context-specific detection (test functions, async functions) to rust_context
    module. Serves as foundation for specialized Rust analyzers (unwrap abuse, clone abuse).

Dependencies: tree-sitter, tree-sitter-rust (optional), src.analyzers.rust_context

Exports: RustBaseAnalyzer class with parsing and traversal utilities,
    TREE_SITTER_RUST_AVAILABLE constant for runtime detection

Interfaces: parse_rust(code), walk_tree(node, node_type), extract_node_text(node),
    is_inside_test(node), is_async_function(node)

Implementation: Tree-sitter parser singleton, recursive AST traversal, composition pattern
    with rust_context helpers

Suppressions:
    - type:ignore[assignment]: Tree-sitter RUST_PARSER fallback when import fails
    - type:ignore[assignment,misc]: Tree-sitter Node type alias (optional dependency fallback)
"""

from typing import Any

from src.analyzers import rust_context

try:
    import tree_sitter_rust as tsrust
    from tree_sitter import Language, Node, Parser

    RUST_LANGUAGE = Language(tsrust.language())
    RUST_PARSER = Parser(RUST_LANGUAGE)
    TREE_SITTER_RUST_AVAILABLE = True
except ImportError:
    TREE_SITTER_RUST_AVAILABLE = False
    RUST_PARSER = None  # type: ignore[assignment]
    Node = Any  # type: ignore[assignment,misc]


class RustBaseAnalyzer:
    """Base analyzer for Rust code using tree-sitter."""

    def __init__(self) -> None:
        """Initialize Rust base analyzer."""
        self.tree_sitter_available = TREE_SITTER_RUST_AVAILABLE

    def parse_rust(self, code: str) -> Node | None:
        """Parse Rust code to AST using tree-sitter.

        Args:
            code: Rust source code to parse

        Returns:
            Tree-sitter AST root node, or None if parsing fails or tree-sitter unavailable
        """
        if not TREE_SITTER_RUST_AVAILABLE or RUST_PARSER is None:
            return None

        tree = RUST_PARSER.parse(bytes(code, "utf8"))
        return tree.root_node

    def walk_tree(self, node: Node, node_type: str) -> list[Node]:
        """Find all nodes of a specific type in the AST.

        Recursively walks the tree and collects all nodes matching the given type.

        Args:
            node: Root tree-sitter node to search from
            node_type: Tree-sitter node type to find (e.g., "function_item")

        Returns:
            List of all matching nodes
        """
        if not TREE_SITTER_RUST_AVAILABLE or node is None:
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

    def extract_identifier_name(self, node: Node) -> str:
        """Extract identifier name from node children.

        Common pattern for extracting names from function/struct declarations.

        Args:
            node: Node to extract identifier from

        Returns:
            Identifier name or "anonymous" fallback
        """
        for child in node.children:
            if child.type == "identifier":
                return self.extract_node_text(child)
        return "anonymous"

    def is_inside_test(self, node: Node) -> bool:
        """Check if node is inside a test function or module.

        Delegates to rust_context module for implementation.

        Args:
            node: Tree-sitter node to check

        Returns:
            True if the node is inside a test function or test module
        """
        return rust_context.is_inside_test(node)

    def is_async_function(self, node: Node) -> bool:
        """Check if a function_item is async.

        Delegates to rust_context module for implementation.

        Args:
            node: Function item node to check

        Returns:
            True if the function is declared as async
        """
        return rust_context.is_async_function(node)

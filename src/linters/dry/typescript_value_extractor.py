"""
Purpose: Extract value representations from TypeScript AST nodes

Scope: Helper for TypeScript constant extraction to extract value strings

Overview: Provides utility methods to extract string representations from tree-sitter AST nodes
    for TypeScript value types (numbers, strings, booleans, arrays, objects, call expressions).
    Used by TypeScriptConstantExtractor to get value context for duplicate constant detection.

Dependencies: tree-sitter, tree-sitter-typescript, src.analyzers.typescript_base

Exports: TypeScriptValueExtractor class

Interfaces: TypeScriptValueExtractor.get_value_string(node, content) -> str | None

Implementation: Tree-sitter node traversal with type-specific string formatting

Suppressions:
    - type:ignore[assignment,misc]: Tree-sitter Node type alias (optional dependency fallback)
"""

from typing import Any

from src.analyzers.typescript_base import TREE_SITTER_AVAILABLE

if TREE_SITTER_AVAILABLE:
    from tree_sitter import Node
else:
    Node = Any  # type: ignore[assignment,misc]


class TypeScriptValueExtractor:
    """Extracts value representations from TypeScript AST nodes."""

    # Types that return their literal text
    LITERAL_TYPES = frozenset(("number", "string", "true", "false", "null", "identifier"))

    # Types with fixed representations
    FIXED_REPRESENTATIONS = {"array": "[...]", "object": "{...}"}

    def get_node_text(self, node: Node, content: str) -> str:
        """Get text content of a node."""
        return content[node.start_byte : node.end_byte]

    def get_value_string(self, node: Node, content: str) -> str | None:
        """Get string representation of a value node."""
        if node.type in self.LITERAL_TYPES:
            return self.get_node_text(node, content)
        if node.type in self.FIXED_REPRESENTATIONS:
            return self.FIXED_REPRESENTATIONS[node.type]
        if node.type == "call_expression":
            return self._get_call_string(node, content)
        return None

    def _get_call_string(self, node: Node, content: str) -> str:
        """Get string representation of a call expression.

        Args:
            node: call_expression node
            content: Original source content

        Returns:
            String like "functionName(...)"
        """
        for child in node.children:
            if child.type == "identifier":
                func_name = self.get_node_text(child, content)
                return f"{func_name}(...)"
        return "call(...)"

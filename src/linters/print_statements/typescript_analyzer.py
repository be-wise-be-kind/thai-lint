"""
Purpose: TypeScript/JavaScript console.* call detection using Tree-sitter AST analysis

Scope: TypeScript and JavaScript console statement detection

Overview: Analyzes TypeScript and JavaScript code to detect console.* method calls that should
    be replaced with proper logging. Uses Tree-sitter parser to traverse TypeScript/JavaScript
    AST and identify call expressions where the callee is console.log, console.warn, console.error,
    console.debug, or console.info (configurable). Returns structured data with the node, method
    name, and line number for each detected console call. Supports both TypeScript and JavaScript
    files with shared detection logic. Handles member expression pattern matching to identify
    console object method calls.

Dependencies: TypeScriptBaseAnalyzer for tree-sitter parsing infrastructure, tree-sitter Node type, logging module

Exports: TypeScriptPrintStatementAnalyzer class

Interfaces: find_console_calls(root_node, methods) -> list[tuple[Node, str, int]]

Implementation: Tree-sitter node traversal with call_expression and member_expression pattern matching
"""

import logging
from typing import Any

from src.analyzers.typescript_base import TypeScriptBaseAnalyzer

logger = logging.getLogger(__name__)

# dry: ignore-block - tree-sitter import pattern (common across TypeScript analyzers)
try:
    from tree_sitter import Node

    TREE_SITTER_AVAILABLE = True
except ImportError:
    TREE_SITTER_AVAILABLE = False
    Node = Any  # type: ignore


class TypeScriptPrintStatementAnalyzer(TypeScriptBaseAnalyzer):
    """Analyzes TypeScript/JavaScript code for console.* calls using Tree-sitter."""

    def __init__(self) -> None:  # pylint: disable=useless-parent-delegation
        """Initialize the TypeScript print statement analyzer."""
        super().__init__()  # Sets self.tree_sitter_available from base class

    def find_console_calls(self, root_node: Node, methods: set[str]) -> list[tuple[Node, str, int]]:
        """Find all console.* calls matching the specified methods.

        Args:
            root_node: Root tree-sitter node to search from
            methods: Set of console method names to detect (e.g., {"log", "warn"})

        Returns:
            List of (node, method_name, line_number) tuples for each console call
        """
        logger.debug(
            "find_console_calls: TREE_SITTER_AVAILABLE=%s, root_node=%s",
            TREE_SITTER_AVAILABLE,
            root_node is not None,
        )
        if not TREE_SITTER_AVAILABLE or root_node is None:
            logger.debug("Early return: tree-sitter not available or root_node is None")
            return []

        calls: list[tuple[Node, str, int]] = []
        self._collect_console_calls(root_node, methods, calls)
        logger.debug("find_console_calls: found %d calls", len(calls))
        return calls

    def _collect_console_calls(
        self, node: Node, methods: set[str], calls: list[tuple[Node, str, int]]
    ) -> None:
        """Recursively collect console.* calls from AST.

        Args:
            node: Current tree-sitter node
            methods: Set of console method names to detect
            calls: List to accumulate found calls
        """
        if node.type == "call_expression":
            method_name = self._extract_console_method(node, methods)
            if method_name is not None:
                line_number = node.start_point[0] + 1
                calls.append((node, method_name, line_number))

        for child in node.children:
            self._collect_console_calls(child, methods, calls)

    def _extract_console_method(self, node: Node, methods: set[str]) -> str | None:
        """Extract console method name if this is a console.* call.

        Args:
            node: Tree-sitter call_expression node
            methods: Set of console method names to detect

        Returns:
            Method name if this is a matching console call, None otherwise
        """
        func_node = self.find_child_by_type(node, "member_expression")
        if func_node is None:
            return None
        if not self._is_console_object(func_node):
            return None
        return self._get_matching_method(func_node, methods)

    def _is_console_object(self, func_node: Node) -> bool:
        """Check if the member expression is on 'console' object."""
        object_node = self._find_object_node(func_node)
        if object_node is None:
            return False
        return self.extract_node_text(object_node) == "console"

    def _get_matching_method(self, func_node: Node, methods: set[str]) -> str | None:
        """Get method name if it matches the configured methods."""
        method_node = self.find_child_by_type(func_node, "property_identifier")
        if method_node is None:
            return None
        method_name = self.extract_node_text(method_node)
        return method_name if method_name in methods else None

    def _find_object_node(self, member_expr: Node) -> Node | None:
        """Find the object node in a member expression.

        Args:
            member_expr: Tree-sitter member_expression node

        Returns:
            Object node (identifier) or None
        """
        for child in member_expr.children:
            if child.type == "identifier":
                return child
        return None

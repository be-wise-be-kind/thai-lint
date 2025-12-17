"""
Purpose: Extract function information from TypeScript AST nodes

Scope: Identifies and extracts function metadata from tree-sitter nodes

Overview: Provides function extraction functionality for TypeScript AST analysis. Extends
    TypeScriptBaseAnalyzer to reuse tree-sitter utilities. Handles multiple TypeScript
    function forms including function declarations, arrow functions, method definitions,
    and function expressions. Extracts function name and node for each form. Recursively
    collects all functions in an AST tree. Isolates function identification logic from
    nesting depth calculation.

Dependencies: TypeScriptBaseAnalyzer, tree-sitter

Exports: TypeScriptFunctionExtractor

Interfaces: extract_function_info(node) -> (node, name), collect_all_functions(root_node) -> list

Implementation: Inherits tree-sitter utilities from base, pattern matching on node types
"""

from typing import Any

from src.analyzers.typescript_base import TypeScriptBaseAnalyzer


class TypeScriptFunctionExtractor(TypeScriptBaseAnalyzer):
    """Extracts function information from TypeScript AST nodes."""

    def __init__(self) -> None:  # pylint: disable=useless-parent-delegation
        """Initialize the TypeScript function extractor."""
        super().__init__()  # Sets self.tree_sitter_available from base class

    def collect_all_functions(self, root_node: Any) -> list[tuple[Any, str]]:
        """Collect all function nodes from TypeScript AST.

        Args:
            root_node: Root tree-sitter node to search

        Returns:
            List of (function_node, function_name) tuples
        """
        functions: list[tuple[Any, str]] = []
        self._collect_functions_recursive(root_node, functions)
        return functions

    def _collect_functions_recursive(self, node: Any, functions: list[tuple[Any, str]]) -> None:
        """Recursively collect function nodes.

        Args:
            node: Current node to examine
            functions: List to append found functions to
        """
        func_info = self.extract_function_info(node)
        if func_info:
            functions.append(func_info)

        for child in node.children:
            self._collect_functions_recursive(child, functions)

    def extract_function_info(self, node: Any) -> tuple[Any, str] | None:
        """Extract function information if node is a function.

        Args:
            node: Tree-sitter node to check

        Returns:
            Tuple of (function_node, function_name) or None
        """
        if node.type == "function_declaration":
            return self._extract_function_declaration(node)
        if node.type == "arrow_function":
            return self._extract_arrow_function(node)
        if node.type == "method_definition":
            return self._extract_method_definition(node)
        if node.type == "function":
            return self._extract_function_expression(node)
        return None

    def _extract_function_declaration(self, node: Any) -> tuple[Any, str]:
        """Extract name from function declaration.

        Args:
            node: function_declaration node

        Returns:
            Tuple of (node, function_name)
        """
        name = self.extract_identifier_name(node)
        return node, name

    def _extract_arrow_function(self, node: Any) -> tuple[Any, str]:
        """Extract name from arrow function (usually anonymous).

        Args:
            node: arrow_function node

        Returns:
            Tuple of (node, "arrow_function" or variable name)
        """
        parent = node.parent
        if not (parent and parent.type == "variable_declarator"):
            return node, "arrow_function"

        name = self.extract_identifier_name(parent)
        return node, name if name != "anonymous" else "arrow_function"

    def _extract_method_definition(self, node: Any) -> tuple[Any, str]:
        """Extract name from method definition.

        Args:
            node: method_definition node

        Returns:
            Tuple of (node, method_name)
        """
        name = self.extract_identifier_name(node)
        return node, name

    def _extract_function_expression(self, node: Any) -> tuple[Any, str]:
        """Extract name from function expression.

        Args:
            node: function expression node

        Returns:
            Tuple of (node, function_name or "function_expression")
        """
        parent = node.parent
        if not (parent and parent.type == "variable_declarator"):
            return node, "function_expression"

        name = self.extract_identifier_name(parent)
        return node, name if name != "anonymous" else "function_expression"

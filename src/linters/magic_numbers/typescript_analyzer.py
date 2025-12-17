"""
Purpose: TypeScript/JavaScript magic number detection using Tree-sitter AST analysis

Scope: Tree-sitter based numeric literal detection for TypeScript and JavaScript code

Overview: Analyzes TypeScript and JavaScript code to detect numeric literals that should be
    extracted to named constants. Uses Tree-sitter parser to traverse TypeScript AST and
    identify numeric literal nodes with their line numbers and values. Detects acceptable
    contexts such as enum definitions and UPPERCASE constant declarations to avoid false
    positives. Supports both TypeScript and JavaScript files with shared detection logic.
    Handles TypeScript-specific syntax including enums, const assertions, readonly properties,
    arrow functions, async functions, and class methods.

Dependencies: TypeScriptBaseAnalyzer for tree-sitter parsing, tree-sitter Node type

Exports: TypeScriptMagicNumberAnalyzer class with find_numeric_literals and context detection

Interfaces: find_numeric_literals(root_node) -> list[tuple], is_enum_context(node),
    is_constant_definition(node)

Implementation: Tree-sitter node traversal with visitor pattern, context-aware filtering
    for acceptable numeric literal locations
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


class TypeScriptMagicNumberAnalyzer(TypeScriptBaseAnalyzer):  # thailint: ignore[srp]
    """Analyzes TypeScript/JavaScript code for magic numbers using Tree-sitter.

    Note: Method count (11) exceeds SRP limit (8) because refactoring for A-grade
    complexity requires extracting helper methods. Class maintains single responsibility
    of TypeScript magic number detection - all methods support this core purpose.
    """

    def __init__(self) -> None:  # pylint: disable=useless-parent-delegation
        """Initialize the TypeScript magic number analyzer."""
        super().__init__()  # Sets self.tree_sitter_available from base class

    def find_numeric_literals(self, root_node: Node) -> list[tuple[Node, float | int, int]]:
        """Find all numeric literal nodes in TypeScript/JavaScript AST.

        Args:
            root_node: Root tree-sitter node to search from

        Returns:
            List of (node, value, line_number) tuples for each numeric literal
        """
        if not TREE_SITTER_AVAILABLE or root_node is None:
            return []

        literals: list[tuple[Node, float | int, int]] = []
        self._collect_numeric_literals(root_node, literals)
        return literals

    def _collect_numeric_literals(
        self, node: Node, literals: list[tuple[Node, float | int, int]]
    ) -> None:
        """Recursively collect numeric literals from AST.

        Args:
            node: Current tree-sitter node
            literals: List to accumulate found literals
        """
        if node.type == "number":
            value = self._extract_numeric_value(node)
            if value is not None:
                line_number = node.start_point[0] + 1
                literals.append((node, value, line_number))

        for child in node.children:
            self._collect_numeric_literals(child, literals)

    def _extract_numeric_value(self, node: Node) -> float | int | None:
        """Extract numeric value from number node.

        Args:
            node: Tree-sitter number node

        Returns:
            Numeric value (int or float) or None if parsing fails
        """
        text = self.extract_node_text(node)
        try:
            # Try int first
            if "." not in text and "e" not in text.lower():
                return int(text, 0)  # Handles hex, octal, binary
            # Otherwise float
            return float(text)
        except (ValueError, TypeError):
            return None

    def is_enum_context(self, node: Node) -> bool:
        """Check if numeric literal is in enum definition.

        Args:
            node: Numeric literal node

        Returns:
            True if node is within enum_declaration
        """
        if not TREE_SITTER_AVAILABLE:
            return False

        current = node.parent
        while current is not None:
            if current.type == "enum_declaration":
                return True
            current = current.parent
        return False

    def is_constant_definition(self, node: Node, source_code: str) -> bool:
        """Check if numeric literal is in UPPERCASE constant definition.

        Args:
            node: Numeric literal node
            source_code: Full source code to extract variable names

        Returns:
            True if assigned to UPPERCASE constant variable
        """
        if not TREE_SITTER_AVAILABLE:
            return False

        # Find the declaration parent
        parent = self._find_declaration_parent(node)
        if parent is None:
            return False

        # Check if identifier is UPPERCASE constant
        return self._has_uppercase_identifier(parent)

    def _find_declaration_parent(self, node: Node) -> Node | None:
        """Find the declaration parent node.

        Args:
            node: Starting node

        Returns:
            Declaration parent or None
        """
        parent = node.parent
        if self._is_declaration_type(parent):
            return parent

        # Try grandparent for nested cases
        if parent is not None:
            grandparent = parent.parent
            if self._is_declaration_type(grandparent):
                return grandparent

        return None

    def _is_declaration_type(self, node: Node | None) -> bool:
        """Check if node is a declaration type."""
        if node is None:
            return False
        return node.type in ("variable_declarator", "lexical_declaration", "pair")

    def _has_uppercase_identifier(self, parent_node: Node) -> bool:
        """Check if declaration has UPPERCASE identifier.

        Args:
            parent_node: Declaration parent node

        Returns:
            True if identifier is UPPERCASE
        """
        identifier_node = self._find_identifier_in_declaration(parent_node)
        if identifier_node is None:
            return False

        identifier_text = self.extract_node_text(identifier_node)
        return self._is_uppercase_constant(identifier_text)

    def _find_identifier_in_declaration(self, node: Node) -> Node | None:
        """Find identifier node in variable declaration.

        Args:
            node: Variable declarator or lexical declaration node

        Returns:
            Identifier node or None
        """
        # Walk children looking for identifier
        for child in node.children:
            if child.type in ("identifier", "property_identifier"):
                return child
            # Recursively check children
            result = self._find_identifier_in_declaration(child)
            if result is not None:
                return result
        return None

    def _is_uppercase_constant(self, name: str) -> bool:
        """Check if identifier is UPPERCASE constant style.

        Args:
            name: Identifier name

        Returns:
            True if name is UPPERCASE with optional underscores
        """
        if not name:
            return False
        # Must be at least one letter and all letters must be uppercase
        # Allow underscores and numbers
        letters_only = "".join(c for c in name if c.isalpha())
        if not letters_only:
            return False
        return letters_only.isupper()

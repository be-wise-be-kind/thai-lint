"""
Purpose: Rust magic number detection using tree-sitter AST analysis

Scope: Tree-sitter based numeric literal detection for Rust code

Overview: Analyzes Rust code to detect numeric literals that should be extracted to named
    constants. Uses tree-sitter parser to traverse Rust AST and identify integer_literal
    and float_literal nodes with their line numbers and values. Detects acceptable contexts
    such as const/static definitions and UPPERCASE constant declarations to avoid false
    positives. Handles Rust-specific syntax including const items, static items, and
    array/slice indexing.

Dependencies: RustBaseAnalyzer for tree-sitter parsing, TREE_SITTER_RUST_AVAILABLE

Exports: RustMagicNumberAnalyzer class with find_numeric_literals and context detection

Interfaces: find_numeric_literals(root_node) -> list[tuple], is_constant_definition(node)

Implementation: Tree-sitter node traversal with visitor pattern, context-aware filtering
"""

from typing import Any

from src.analyzers.rust_base import TREE_SITTER_RUST_AVAILABLE, RustBaseAnalyzer


class RustMagicNumberAnalyzer(RustBaseAnalyzer):
    """Analyzes Rust code for magic numbers using tree-sitter."""

    # Node types that represent numeric literals in Rust
    NUMERIC_LITERAL_TYPES = {"integer_literal", "float_literal"}

    def find_numeric_literals(self, root_node: Any) -> list[tuple[Any, float | int, int]]:
        """Find all numeric literal nodes in Rust AST.

        Args:
            root_node: Root tree-sitter node to search from

        Returns:
            List of (node, value, line_number) tuples for each numeric literal
        """
        if not TREE_SITTER_RUST_AVAILABLE or root_node is None:
            return []

        literals: list[tuple[Any, float | int, int]] = []
        self._collect_numeric_literals(root_node, literals)
        return literals

    def _collect_numeric_literals(
        self, node: Any, literals: list[tuple[Any, float | int, int]]
    ) -> None:
        """Recursively collect numeric literals from AST.

        Args:
            node: Current tree-sitter node
            literals: List to accumulate found literals
        """
        if node.type in self.NUMERIC_LITERAL_TYPES:
            value = self._extract_numeric_value(node)
            if value is not None:
                line_number = node.start_point[0] + 1
                literals.append((node, value, line_number))

        for child in node.children:
            self._collect_numeric_literals(child, literals)

    def _extract_numeric_value(self, node: Any) -> float | int | None:
        """Extract numeric value from a literal node.

        Handles Rust integer suffixes (i32, u64, etc.) and various formats.

        Args:
            node: Tree-sitter numeric literal node

        Returns:
            Numeric value (int or float) or None if parsing fails
        """
        text = self.extract_node_text(node)
        # Strip Rust type suffixes (i32, u64, f64, usize, etc.)
        cleaned = self._strip_type_suffix(text)
        # Strip underscores used as visual separators (e.g., 1_000_000)
        cleaned = cleaned.replace("_", "")
        try:
            if node.type == "float_literal":
                return float(cleaned)
            return int(cleaned, 0)  # Handles hex, octal, binary
        except (ValueError, TypeError):
            return None

    def _strip_type_suffix(self, text: str) -> str:
        """Strip Rust numeric type suffixes from literal text.

        Args:
            text: Raw literal text (e.g., "42i32", "3.14f64")

        Returns:
            Text with suffix removed
        """
        suffixes = (
            "u8",
            "u16",
            "u32",
            "u64",
            "u128",
            "usize",
            "i8",
            "i16",
            "i32",
            "i64",
            "i128",
            "isize",
            "f32",
            "f64",
        )
        for suffix in suffixes:
            if text.endswith(suffix):
                return text[: -len(suffix)]
        return text

    def is_constant_definition(self, node: Any) -> bool:
        """Check if numeric literal is in a const or static definition.

        Args:
            node: Numeric literal node

        Returns:
            True if inside const_item or static_item
        """
        if not TREE_SITTER_RUST_AVAILABLE:
            return False

        current = node.parent
        while current is not None:
            if current.type in ("const_item", "static_item"):
                return True
            current = current.parent
        return False

    def is_test_context(self, node: Any) -> bool:
        """Check if numeric literal is inside test code.

        Args:
            node: Numeric literal node

        Returns:
            True if inside #[test] function or #[cfg(test)] module
        """
        return self.is_inside_test(node)

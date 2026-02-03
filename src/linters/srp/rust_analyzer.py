"""
Purpose: Rust AST analyzer for detecting SRP violations in Rust structs

Scope: RustSRPAnalyzer class for analyzing Rust struct + impl block patterns using tree-sitter

Overview: Implements Rust-specific SRP analysis using tree-sitter parser. Extends
    RustBaseAnalyzer to reuse common tree-sitter initialization and traversal patterns.
    Walks the AST to find all struct declarations and impl blocks. Matches impl blocks
    to their corresponding structs by type identifier name. Counts methods across all
    impl blocks for a given struct and calculates total lines of code. Collects
    comprehensive metrics including struct name, method count, LOC, keyword presence,
    and location information. In Rust, a struct + its impl blocks is analogous to a
    class in other languages for SRP analysis purposes.

Dependencies: RustBaseAnalyzer, SRPConfig

Exports: RustSRPAnalyzer class

Interfaces: find_all_structs(root_node), analyze_struct(struct_node, impl_blocks, source, config)

Implementation: Inherits tree-sitter parsing from base, aggregates methods across impl blocks
"""

from typing import Any

from src.analyzers.rust_base import RustBaseAnalyzer

from .config import SRPConfig


class RustSRPAnalyzer(RustBaseAnalyzer):
    """Analyzes Rust structs and impl blocks for SRP violations."""

    def find_all_structs(self, root_node: Any) -> list[Any]:
        """Find all struct declarations in Rust AST.

        Args:
            root_node: Root tree-sitter node to search

        Returns:
            List of all struct_item nodes
        """
        return self.walk_tree(root_node, "struct_item")

    def find_all_impl_blocks(self, root_node: Any) -> list[Any]:
        """Find all impl blocks in Rust AST.

        Args:
            root_node: Root tree-sitter node to search

        Returns:
            List of all impl_item nodes
        """
        return self.walk_tree(root_node, "impl_item")

    def get_impl_target_name(self, impl_node: Any) -> str:
        """Extract the type name that an impl block targets.

        Args:
            impl_node: An impl_item tree-sitter node

        Returns:
            The type identifier name (e.g., "Foo" from "impl Foo {}")
        """
        for child in impl_node.children:
            if child.type == "type_identifier":
                return self.extract_node_text(child)
        return ""

    def count_impl_methods(self, impl_node: Any) -> int:
        """Count function items (methods) in an impl block.

        Counts all function_item children that are public (not prefixed with _).

        Args:
            impl_node: An impl_item tree-sitter node

        Returns:
            Number of public methods in the impl block
        """
        declaration_list = self._find_declaration_list(impl_node)
        if declaration_list is None:
            return 0

        count = 0
        for child in declaration_list.children:
            if child.type == "function_item" and self._is_countable_method(child):
                count += 1
        return count

    def analyze_struct(
        self,
        struct_node: Any,
        impl_blocks: list[Any],
        source: str,
        config: SRPConfig,
    ) -> dict[str, Any]:
        """Analyze a Rust struct and its impl blocks for SRP metrics.

        Args:
            struct_node: Tree-sitter node representing a struct declaration
            impl_blocks: List of impl_item nodes targeting this struct
            source: Full source code of the file
            config: SRP configuration with thresholds and keywords

        Returns:
            Dictionary with struct metrics (class_name, method_count, loc, etc.)
        """
        struct_name = self._extract_type_name(struct_node)
        method_count = self._count_total_methods(impl_blocks)
        loc = self._calculate_loc(struct_node, impl_blocks, source)
        has_keyword = any(keyword in struct_name for keyword in config.keywords)

        return {
            "class_name": struct_name,
            "method_count": method_count,
            "loc": loc,
            "has_keyword": has_keyword,
            "line": struct_node.start_point[0] + 1,
            "column": struct_node.start_point[1],
        }

    def _count_total_methods(self, impl_blocks: list[Any]) -> int:
        """Count methods across all impl blocks.

        Args:
            impl_blocks: List of impl_item nodes for a struct

        Returns:
            Total public method count
        """
        return sum(self.count_impl_methods(impl_node) for impl_node in impl_blocks)

    def _calculate_loc(self, struct_node: Any, impl_blocks: list[Any], source: str) -> int:
        """Calculate lines of code for struct and its impl blocks.

        Args:
            struct_node: Struct declaration node
            impl_blocks: List of impl blocks for this struct
            source: Full source code

        Returns:
            Total lines of code
        """
        struct_loc = self._node_loc(struct_node, source)
        impl_loc = sum(self._node_loc(impl_node, source) for impl_node in impl_blocks)
        return struct_loc + impl_loc

    def _node_loc(self, node: Any, source: str) -> int:
        """Calculate lines of code for a single node.

        Args:
            node: Tree-sitter node
            source: Full source code

        Returns:
            Number of non-blank, non-comment lines
        """
        start_line = node.start_point[0]
        end_line = node.end_point[0]
        lines = source.split("\n")[start_line : end_line + 1]
        return sum(1 for line in lines if line.strip() and not line.strip().startswith("//"))

    def _find_declaration_list(self, impl_node: Any) -> Any:
        """Find the declaration_list node in an impl block.

        Args:
            impl_node: An impl_item tree-sitter node

        Returns:
            The declaration_list child node or None
        """
        for child in impl_node.children:
            if child.type == "declaration_list":
                return child
        return None

    def _extract_type_name(self, node: Any) -> str:
        """Extract type name from a struct or impl node.

        Rust struct declarations use type_identifier instead of identifier.

        Args:
            node: A struct_item or impl_item tree-sitter node

        Returns:
            The type name or "anonymous" fallback
        """
        for child in node.children:
            if child.type == "type_identifier":
                return self.extract_node_text(child)
        return self.extract_identifier_name(node)

    def _is_countable_method(self, func_node: Any) -> bool:
        """Check if a function should be counted as a public method.

        Excludes functions starting with underscore (private convention).

        Args:
            func_node: A function_item tree-sitter node

        Returns:
            True if the function should be counted
        """
        name = self.extract_identifier_name(func_node)
        return not name.startswith("_")

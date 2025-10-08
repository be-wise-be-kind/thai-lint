"""
Purpose: TypeScript AST analyzer for detecting SRP violations in TypeScript classes

Scope: TypeScriptSRPAnalyzer class for analyzing TypeScript classes using tree-sitter

Overview: Implements TypeScript-specific SRP analysis using tree-sitter parser. Walks the AST to
    find all class declarations, analyzes each class for SRP violation indicators using metrics
    calculator helper. Collects comprehensive metrics including class name, method count, LOC,
    keyword presence, and location information. Delegates metrics calculation to TypeScriptMetricsCalculator.

Dependencies: tree-sitter, tree-sitter-typescript, TypeScriptMetricsCalculator, SRPConfig

Exports: TypeScriptSRPAnalyzer class

Interfaces: find_all_classes(tree), analyze_class(class_node, source, config)

Implementation: tree-sitter AST walking, composition with metrics calculator
"""

from typing import Any

try:
    import tree_sitter_typescript as tstypescript
    from tree_sitter import Language, Parser

    TS_LANGUAGE = Language(tstypescript.language_typescript())
    TS_PARSER = Parser(TS_LANGUAGE)
    TREE_SITTER_AVAILABLE = True
except ImportError:
    TREE_SITTER_AVAILABLE = False
    TS_PARSER = None  # type: ignore

from .config import SRPConfig
from .typescript_metrics_calculator import TypeScriptMetricsCalculator


class TypeScriptSRPAnalyzer:
    """Analyzes TypeScript classes for SRP violations."""

    def __init__(self) -> None:
        """Initialize analyzer with metrics calculator."""
        self.metrics_calculator = TypeScriptMetricsCalculator()

    def parse_typescript(self, code: str) -> Any:
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

    def find_all_classes(self, root_node: Any) -> list[Any]:
        """Find all class declarations in TypeScript AST.

        Args:
            root_node: Root tree-sitter node to search

        Returns:
            List of all class declaration nodes
        """
        if not TREE_SITTER_AVAILABLE or root_node is None:
            return []

        classes: list[Any] = []
        self._walk_tree(root_node, classes)
        return classes

    def analyze_class(self, class_node: Any, source: str, config: SRPConfig) -> dict[str, Any]:
        """Analyze a TypeScript class for SRP metrics.

        Args:
            class_node: Tree-sitter node representing a class declaration
            source: Full source code of the file
            config: SRP configuration with thresholds and keywords

        Returns:
            Dictionary with class metrics (name, method_count, loc, etc.)
        """
        class_name = self._get_class_name(class_node)
        method_count = self.metrics_calculator.count_methods(class_node)
        loc = self.metrics_calculator.count_loc(class_node, source)
        has_keyword = any(keyword in class_name for keyword in config.keywords)

        return {
            "class_name": class_name,
            "method_count": method_count,
            "loc": loc,
            "has_keyword": has_keyword,
            "line": class_node.start_point[0] + 1,
            "column": class_node.start_point[1],
        }

    def _walk_tree(self, node: Any, classes: list[Any]) -> None:
        """Recursively walk tree to find class declarations.

        Args:
            node: Current tree-sitter node
            classes: List to accumulate class nodes
        """
        if node.type == "class_declaration":
            classes.append(node)

        for child in node.children:
            self._walk_tree(child, classes)

    def _get_class_name(self, class_node: Any) -> str:
        """Extract class name from class declaration node.

        Args:
            class_node: Class declaration tree-sitter node

        Returns:
            Class name as string, or "UnnamedClass" if not found
        """
        for child in class_node.children:
            if child.type in ("identifier", "type_identifier"):
                return child.text.decode()
        return "UnnamedClass"

"""
Purpose: TypeScript AST analyzer for detecting SRP violations in TypeScript classes

Scope: TypeScriptSRPAnalyzer class for analyzing TypeScript classes using tree-sitter

Overview: Implements TypeScript-specific SRP analysis using tree-sitter parser. Extends
    TypeScriptBaseAnalyzer to reuse common tree-sitter initialization and traversal patterns.
    Walks the AST to find all class declarations, analyzes each class for SRP violation
    indicators using metrics calculator helper. Collects comprehensive metrics including
    class name, method count, LOC, keyword presence, and location information. Delegates
    metrics calculation to TypeScriptMetricsCalculator.

Dependencies: TypeScriptBaseAnalyzer, TypeScriptMetricsCalculator, SRPConfig

Exports: TypeScriptSRPAnalyzer class

Interfaces: find_all_classes(tree), analyze_class(class_node, source, config)

Implementation: Inherits tree-sitter parsing from base, composition with metrics calculator
"""

from typing import Any

from src.analyzers.typescript_base import TypeScriptBaseAnalyzer

from .config import SRPConfig
from .typescript_metrics_calculator import TypeScriptMetricsCalculator


class TypeScriptSRPAnalyzer(TypeScriptBaseAnalyzer):
    """Analyzes TypeScript classes for SRP violations."""

    def __init__(self) -> None:
        """Initialize analyzer with metrics calculator."""
        super().__init__()
        self.metrics_calculator = TypeScriptMetricsCalculator()

    def find_all_classes(self, root_node: Any) -> list[Any]:
        """Find all class declarations in TypeScript AST.

        Args:
            root_node: Root tree-sitter node to search

        Returns:
            List of all class declaration nodes
        """
        return self.walk_tree(root_node, "class_declaration")

    def analyze_class(self, class_node: Any, source: str, config: SRPConfig) -> dict[str, Any]:
        """Analyze a TypeScript class for SRP metrics.

        Args:
            class_node: Tree-sitter node representing a class declaration
            source: Full source code of the file
            config: SRP configuration with thresholds and keywords

        Returns:
            Dictionary with class metrics (name, method_count, loc, etc.)
        """
        class_name = self.extract_identifier_name(class_node)
        if class_name == "anonymous":
            class_name = "UnnamedClass"

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

"""
Purpose: Python AST analyzer for detecting SRP violations in Python classes

Scope: Functions for analyzing Python classes using AST

Overview: Implements Python-specific SRP analysis using the ast module to parse and analyze
    class definitions. Walks the AST to find all class definitions, then analyzes each class
    for SRP violation indicators: method count, lines of code, and responsibility keywords.
    Collects comprehensive metrics including class name, method count, LOC, keyword presence,
    and location information (line, column). Integrates with heuristics module for metric
    calculation. Returns structured metric dictionaries that the main linter uses to create
    violations. Handles nested classes by analyzing all classes in the tree.

Dependencies: ast module for Python AST parsing, typing for type hints, heuristics module

Exports: find_all_classes function, analyze_class function, PythonSRPAnalyzer class (compat)

Interfaces: find_all_classes(tree), analyze_class(class_node, source, config)

Implementation: AST walking pattern, metric collection, integration with heuristics module
"""

import ast
from typing import Any

from .config import SRPConfig
from .heuristics import count_loc, count_methods, has_responsibility_keyword


def find_all_classes(tree: ast.AST) -> list[ast.ClassDef]:
    """Find all class definitions in AST.

    Args:
        tree: Root AST node to search

    Returns:
        List of all class definition nodes
    """
    classes = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            classes.append(node)
    return classes


def analyze_class(class_node: ast.ClassDef, source: str, config: SRPConfig) -> dict[str, Any]:
    """Analyze a class for SRP metrics.

    Args:
        class_node: AST node representing a class definition
        source: Full source code of the file
        config: SRP configuration with thresholds and keywords

    Returns:
        Dictionary with class metrics (name, method_count, loc, etc.)
    """
    method_count = count_methods(class_node)
    loc = count_loc(class_node, source)
    has_keyword = has_responsibility_keyword(class_node.name, config.keywords)

    return {
        "class_name": class_node.name,
        "method_count": method_count,
        "loc": loc,
        "has_keyword": has_keyword,
        "line": class_node.lineno,
        "column": class_node.col_offset,
    }


# Legacy class wrapper for backward compatibility
class PythonSRPAnalyzer:
    """Analyzes Python classes for SRP violations.

    Note: This class is a thin wrapper around module-level functions
    for backward compatibility.
    """

    def __init__(self) -> None:
        """Initialize the analyzer."""
        pass  # No state needed

    def find_all_classes(self, tree: ast.AST) -> list[ast.ClassDef]:
        """Find all class definitions in AST.

        Args:
            tree: Root AST node to search

        Returns:
            List of all class definition nodes
        """
        return find_all_classes(tree)

    def analyze_class(
        self, class_node: ast.ClassDef, source: str, config: SRPConfig
    ) -> dict[str, Any]:
        """Analyze a class for SRP metrics.

        Args:
            class_node: AST node representing a class definition
            source: Full source code of the file
            config: SRP configuration with thresholds and keywords

        Returns:
            Dictionary with class metrics (name, method_count, loc, etc.)
        """
        return analyze_class(class_node, source, config)

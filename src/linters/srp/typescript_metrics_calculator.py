"""
Purpose: TypeScript class metrics calculation for SRP analysis

Scope: Calculates method count and lines of code for TypeScript classes

Overview: Provides metrics calculation functionality for TypeScript classes in SRP analysis. Counts
    public methods in class bodies (excludes constructors), calculates lines of code from AST node
    positions, and identifies class body nodes. Uses tree-sitter AST node types. Isolates metrics
    calculation from class analysis and tree traversal logic.

Dependencies: typing

Exports: count_methods function, count_loc function, TypeScriptMetricsCalculator class (compat)

Interfaces: count_methods(class_node), count_loc(class_node, source)

Implementation: Tree-sitter node type matching, AST position arithmetic
"""

from typing import Any


def count_methods(class_node: Any) -> int:
    """Count number of methods in a TypeScript class.

    Args:
        class_node: Class declaration tree-sitter node

    Returns:
        Number of public methods (excludes constructor)
    """
    class_body = _get_class_body(class_node)
    if not class_body:
        return 0

    method_count = 0
    for child in class_body.children:
        if _is_countable_method(child):
            method_count += 1

    return method_count


def count_loc(class_node: Any, source: str) -> int:
    """Count lines of code in a TypeScript class.

    Args:
        class_node: Class declaration tree-sitter node
        source: Full source code string

    Returns:
        Number of lines in class definition
    """
    start_line = class_node.start_point[0]
    end_line = class_node.end_point[0]
    return end_line - start_line + 1


def _get_class_body(class_node: Any) -> Any:
    """Get the class_body node from a class declaration.

    Args:
        class_node: Class declaration node

    Returns:
        Class body node or None
    """
    for child in class_node.children:
        if child.type == "class_body":
            return child
    return None


def _is_countable_method(node: Any) -> bool:
    """Check if node is a method that should be counted.

    Args:
        node: Tree-sitter node to check

    Returns:
        True if node is a countable method
    """
    if node.type != "method_definition":
        return False

    # Check if it's a constructor
    return all(
        not (child.type == "property_identifier" and child.text.decode() == "constructor")
        for child in node.children
    )


# Legacy class wrapper for backward compatibility
class TypeScriptMetricsCalculator:
    """Calculates metrics for TypeScript classes.

    Note: This class is a thin wrapper around module-level functions
    for backward compatibility.
    """

    def __init__(self) -> None:
        """Initialize the metrics calculator."""
        pass  # No state needed

    def count_methods(self, class_node: Any) -> int:
        """Count number of methods in a TypeScript class.

        Args:
            class_node: Class declaration tree-sitter node

        Returns:
            Number of public methods (excludes constructor)
        """
        return count_methods(class_node)

    def count_loc(self, class_node: Any, source: str) -> int:
        """Count lines of code in a TypeScript class.

        Args:
            class_node: Class declaration tree-sitter node
            source: Full source code string

        Returns:
            Number of lines in class definition
        """
        return count_loc(class_node, source)

"""
Purpose: SRP detection heuristics for analyzing code complexity and responsibility

Scope: Helper functions for method counting, LOC calculation, and keyword detection

Overview: Provides heuristic-based analysis functions for detecting Single Responsibility
    Principle violations. Implements method counting that excludes property decorators and
    special methods. Provides LOC calculation that filters out blank lines and comments.
    Includes keyword detection for identifying generic class names that often indicate SRP
    violations (Manager, Handler, etc.). Supports both Python AST and TypeScript tree-sitter
    nodes. These heuristics enable practical SRP detection without requiring perfect semantic
    analysis, focusing on measurable code metrics that correlate with responsibility scope.

Dependencies: ast module for Python AST analysis, typing for type hints

Exports: count_methods, count_loc, has_responsibility_keyword, has_property_decorator

Interfaces: Functions accepting AST nodes and returning metrics (int, bool)

Implementation: AST walking with filtering logic, heuristic-based thresholds
"""

import ast


def count_methods(class_node: ast.ClassDef) -> int:
    """Count methods in a class (excludes properties and special methods).

    Args:
        class_node: AST node representing a class definition

    Returns:
        Number of methods in the class
    """
    methods = 0
    func_nodes = (
        n for n in class_node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
    )
    for node in func_nodes:
        # Don't count @property decorators as methods
        if not has_property_decorator(node):
            methods += 1
    return methods


def count_loc(class_node: ast.ClassDef, source: str) -> int:
    """Count lines of code in a class (excludes blank lines and comments).

    Args:
        class_node: AST node representing a class definition
        source: Full source code of the file

    Returns:
        Number of code lines in the class
    """
    start_line = class_node.lineno
    end_line = class_node.end_lineno or start_line
    lines = source.split("\n")[start_line - 1 : end_line]

    # Filter out blank lines and comments
    code_lines = [line for line in lines if line.strip() and not line.strip().startswith("#")]
    return len(code_lines)


def has_responsibility_keyword(class_name: str, keywords: list[str]) -> bool:
    """Check if class name contains responsibility keywords.

    Args:
        class_name: Name of the class to check
        keywords: List of keywords indicating potential SRP violations

    Returns:
        True if class name contains any responsibility keyword
    """
    return any(keyword in class_name for keyword in keywords)


def has_property_decorator(func_node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """Check if function has @property decorator.

    Args:
        func_node: AST node representing a function definition

    Returns:
        True if function has @property decorator
    """
    for decorator in func_node.decorator_list:
        if isinstance(decorator, ast.Name) and decorator.id == "property":
            return True
    return False

"""
Purpose: Python AST analyzer for detecting stateless classes

Scope: AST-based analysis of Python class definitions for stateless patterns

Overview: Analyzes Python source code using AST to detect classes that have no
    constructor (__init__ or __new__), no instance state (self.attr assignments),
    and 2+ methods - indicating they should be refactored to module-level functions.
    Excludes legitimate patterns like ABC, Protocol, decorated classes, and classes
    with class-level attributes.

Dependencies: Python AST module

Exports: analyze_code function, ClassInfo dataclass

Interfaces: analyze_code(code) -> list[ClassInfo] returning detected stateless classes

Implementation: AST visitor pattern with focused helper functions for different checks
"""

import ast
from dataclasses import dataclass


@dataclass
class ClassInfo:
    """Information about a detected stateless class."""

    name: str
    line: int
    column: int


def analyze_code(code: str, min_methods: int = 2) -> list[ClassInfo]:
    """Analyze Python code for stateless classes.

    Args:
        code: Python source code
        min_methods: Minimum methods required to flag class

    Returns:
        List of detected stateless class info
    """
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return []

    return _find_stateless_classes(tree, min_methods)


def _find_stateless_classes(tree: ast.Module, min_methods: int = 2) -> list[ClassInfo]:
    """Find all stateless classes in AST.

    Args:
        tree: Parsed AST module
        min_methods: Minimum methods required to flag class

    Returns:
        List of stateless class info
    """
    results = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and _is_stateless(node, min_methods):
            results.append(ClassInfo(node.name, node.lineno, node.col_offset))
    return results


def _is_stateless(class_node: ast.ClassDef, min_methods: int = 2) -> bool:
    """Check if class is stateless and should be functions.

    Args:
        class_node: AST ClassDef node
        min_methods: Minimum methods required to flag class

    Returns:
        True if class is stateless violation
    """
    if _should_skip_class(class_node):
        return False
    return _count_methods(class_node) >= min_methods


def _should_skip_class(class_node: ast.ClassDef) -> bool:
    """Check if class should be skipped from analysis.

    Args:
        class_node: AST ClassDef node

    Returns:
        True if class should be skipped
    """
    return (
        _has_constructor(class_node)
        or _is_exception_case(class_node)
        or _has_class_attributes(class_node)
        or _has_instance_attributes(class_node)
        or _has_base_classes(class_node)
    )


def _has_base_classes(class_node: ast.ClassDef) -> bool:
    """Check if class inherits from non-trivial base classes.

    Classes that inherit from other classes are using polymorphism/inheritance
    and should not be flagged as stateless.

    Args:
        class_node: AST ClassDef node

    Returns:
        True if class has non-trivial base classes
    """
    if not class_node.bases:
        return False

    for base in class_node.bases:
        base_name = _get_base_name(base)
        # Skip trivial bases like object
        if base_name and base_name not in ("object",):
            return True

    return False


def _count_methods(class_node: ast.ClassDef) -> int:
    """Count methods in class.

    Args:
        class_node: AST ClassDef node

    Returns:
        Number of methods
    """
    return sum(1 for item in class_node.body if isinstance(item, ast.FunctionDef))


def _has_constructor(class_node: ast.ClassDef) -> bool:
    """Check if class has __init__ or __new__ method.

    Args:
        class_node: AST ClassDef node

    Returns:
        True if class has constructor
    """
    constructor_names = ("__init__", "__new__")
    for item in class_node.body:
        if isinstance(item, ast.FunctionDef) and item.name in constructor_names:
            return True
    return False


def _is_exception_case(class_node: ast.ClassDef) -> bool:
    """Check if class is an exception case (ABC, Protocol, or decorated).

    Args:
        class_node: AST ClassDef node

    Returns:
        True if class is ABC, Protocol, or decorated
    """
    if class_node.decorator_list:
        return True
    return _inherits_from_abc_or_protocol(class_node)


def _inherits_from_abc_or_protocol(class_node: ast.ClassDef) -> bool:
    """Check if class inherits from ABC or Protocol.

    Args:
        class_node: AST ClassDef node

    Returns:
        True if inherits from ABC or Protocol
    """
    for base in class_node.bases:
        if _get_base_name(base) in ("ABC", "Protocol"):
            return True
    return False


def _get_base_name(base: ast.expr) -> str:
    """Extract name from base class expression.

    Args:
        base: AST expression for base class

    Returns:
        Base class name or empty string
    """
    if isinstance(base, ast.Name):
        return base.id
    if isinstance(base, ast.Attribute):
        return base.attr
    return ""


def _has_class_attributes(class_node: ast.ClassDef) -> bool:
    """Check if class has class-level attributes.

    Args:
        class_node: AST ClassDef node

    Returns:
        True if class has class attributes
    """
    for item in class_node.body:
        if isinstance(item, (ast.Assign, ast.AnnAssign)):
            return True
    return False


def _has_instance_attributes(class_node: ast.ClassDef) -> bool:
    """Check if methods assign to self.attr.

    Args:
        class_node: AST ClassDef node

    Returns:
        True if any method assigns to self
    """
    for item in class_node.body:
        if isinstance(item, ast.FunctionDef) and _method_has_self_assignment(item):
            return True
    return False


def _method_has_self_assignment(method: ast.FunctionDef) -> bool:
    """Check if method assigns to self.attr.

    Args:
        method: AST FunctionDef node

    Returns:
        True if method assigns to self
    """
    for node in ast.walk(method):
        if _is_self_attribute_assignment(node):
            return True
    return False


def _is_self_attribute_assignment(node: ast.AST) -> bool:
    """Check if node is a self.attr assignment.

    Args:
        node: AST node to check

    Returns:
        True if node is self attribute assignment
    """
    if not isinstance(node, ast.Assign):
        return False
    return any(_is_self_attribute(t) for t in node.targets)


def _is_self_attribute(node: ast.expr) -> bool:
    """Check if node is a self.attr reference.

    Args:
        node: AST expression node

    Returns:
        True if node is self.attr
    """
    if not isinstance(node, ast.Attribute):
        return False
    if not isinstance(node.value, ast.Name):
        return False
    return node.value.id == "self"


# Legacy class wrapper for backward compatibility with linter.py
class StatelessClassAnalyzer:
    """Analyzes Python code for stateless classes.

    Note: This class is a thin wrapper around module-level functions
    to maintain backward compatibility with existing code.
    """

    def __init__(self, min_methods: int = 2) -> None:
        """Initialize the analyzer.

        Args:
            min_methods: Minimum methods required to flag class
        """
        self._min_methods = min_methods

    def analyze(self, code: str) -> list[ClassInfo]:
        """Analyze Python code for stateless classes.

        Args:
            code: Python source code

        Returns:
            List of detected stateless class info
        """
        return analyze_code(code, self._min_methods)

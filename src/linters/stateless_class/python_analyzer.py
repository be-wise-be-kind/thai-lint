"""
Purpose: Python AST analyzer for detecting stateless classes

Scope: AST-based analysis of Python class definitions for stateless patterns

Overview: Analyzes Python source code using AST to detect classes that have no
    constructor (__init__ or __new__), no instance state (self.attr assignments),
    and 2+ methods - indicating they should be refactored to module-level functions.
    Excludes legitimate patterns like ABC, Protocol, decorated classes, and classes
    with class-level attributes.

Dependencies: Python AST module

Exports: StatelessClassAnalyzer class

Interfaces: analyze(code) -> list[ClassInfo] returning detected stateless classes

Implementation: AST visitor pattern with focused helper classes for different checks
"""

import ast
from dataclasses import dataclass


@dataclass
class ClassInfo:
    """Information about a detected stateless class."""

    name: str
    line: int
    column: int


class StatelessClassAnalyzer:
    """Analyzes Python code for stateless classes."""

    def analyze(self, code: str) -> list[ClassInfo]:
        """Analyze Python code for stateless classes.

        Args:
            code: Python source code

        Returns:
            List of detected stateless class info
        """
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return []

        return self._find_stateless_classes(tree)

    def _find_stateless_classes(self, tree: ast.Module) -> list[ClassInfo]:
        """Find all stateless classes in AST.

        Args:
            tree: Parsed AST module

        Returns:
            List of stateless class info
        """
        results = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and self._is_stateless(node):
                results.append(ClassInfo(node.name, node.lineno, node.col_offset))
        return results

    def _is_stateless(self, class_node: ast.ClassDef) -> bool:
        """Check if class is stateless and should be functions.

        Args:
            class_node: AST ClassDef node

        Returns:
            True if class is stateless violation
        """
        if self._should_skip_class(class_node):
            return False
        return self._count_methods(class_node) >= 2

    def _should_skip_class(self, class_node: ast.ClassDef) -> bool:
        """Check if class should be skipped from analysis.

        Args:
            class_node: AST ClassDef node

        Returns:
            True if class should be skipped
        """
        checker = ClassChecker(class_node)
        return (
            checker.has_constructor()
            or checker.is_exception_case()
            or checker.has_class_attributes()
            or checker.has_instance_attributes()
        )

    def _count_methods(self, class_node: ast.ClassDef) -> int:
        """Count methods in class.

        Args:
            class_node: AST ClassDef node

        Returns:
            Number of methods
        """
        return sum(1 for item in class_node.body if isinstance(item, ast.FunctionDef))


class ClassChecker:
    """Performs various checks on a class AST node."""

    def __init__(self, class_node: ast.ClassDef) -> None:
        """Initialize checker with class node.

        Args:
            class_node: AST ClassDef node to check
        """
        self._node = class_node

    def has_constructor(self) -> bool:
        """Check if class has __init__ or __new__ method.

        Returns:
            True if class has constructor
        """
        constructor_names = ("__init__", "__new__")
        for item in self._node.body:
            if isinstance(item, ast.FunctionDef) and item.name in constructor_names:
                return True
        return False

    def is_exception_case(self) -> bool:
        """Check if class is an exception case (ABC, Protocol, or decorated).

        Returns:
            True if class is ABC, Protocol, or decorated
        """
        if self._node.decorator_list:
            return True
        return self._inherits_from_abc_or_protocol()

    def _inherits_from_abc_or_protocol(self) -> bool:
        """Check if class inherits from ABC or Protocol.

        Returns:
            True if inherits from ABC or Protocol
        """
        for base in self._node.bases:
            if self._get_base_name(base) in ("ABC", "Protocol"):
                return True
        return False

    def _get_base_name(self, base: ast.expr) -> str:
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

    def has_class_attributes(self) -> bool:
        """Check if class has class-level attributes.

        Returns:
            True if class has class attributes
        """
        for item in self._node.body:
            if isinstance(item, (ast.Assign, ast.AnnAssign)):
                return True
        return False

    def has_instance_attributes(self) -> bool:
        """Check if methods assign to self.attr.

        Returns:
            True if any method assigns to self
        """
        for item in self._node.body:
            if isinstance(item, ast.FunctionDef) and self._method_uses_self(item):
                return True
        return False

    def _method_uses_self(self, method: ast.FunctionDef) -> bool:
        """Check if method assigns to self.attr.

        Args:
            method: AST FunctionDef node

        Returns:
            True if method assigns to self
        """
        checker = SelfAttributeChecker()
        return checker.has_self_assignment(method)


class SelfAttributeChecker:
    """Checks for self.attr assignments in methods."""

    def has_self_assignment(self, method: ast.FunctionDef) -> bool:
        """Check if method assigns to self.attr.

        Args:
            method: AST FunctionDef node

        Returns:
            True if method assigns to self
        """
        for node in ast.walk(method):
            if self._is_self_attribute_assignment(node):
                return True
        return False

    def _is_self_attribute_assignment(self, node: ast.AST) -> bool:
        """Check if node is a self.attr assignment.

        Args:
            node: AST node to check

        Returns:
            True if node is self attribute assignment
        """
        if not isinstance(node, ast.Assign):
            return False
        return any(self._is_self_attribute(t) for t in node.targets)

    def _is_self_attribute(self, node: ast.expr) -> bool:
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

"""
Purpose: Stateless class linter package for detecting classes without state

Scope: Python classes that should be refactored to module-level functions

Overview: Package for detecting Python classes that have no constructor (__init__
    or __new__) and no instance state (self.attr assignments), indicating they should
    be refactored to module-level functions. Identifies a common anti-pattern in
    AI-generated code where classes are used as namespaces rather than for object-
    oriented encapsulation.

Dependencies: Python AST module, base linter framework

Exports: StatelessClassRule - main rule for detecting stateless classes

Interfaces: StatelessClassRule.check(context) -> list[Violation]

Implementation: AST-based analysis checking for constructor methods and instance
    attribute assignments while excluding legitimate patterns (ABC, Protocol, decorators)
"""

from .linter import StatelessClassRule
from .python_analyzer import ClassInfo, StatelessClassAnalyzer

__all__ = ["StatelessClassRule", "StatelessClassAnalyzer", "ClassInfo"]

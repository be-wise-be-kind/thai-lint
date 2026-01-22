"""
Purpose: Base class for LBYL pattern detectors

Scope: Abstract base providing common detector interface

Overview: Defines BaseLBYLDetector abstract class that all pattern detectors extend.
    Inherits from ast.NodeVisitor for AST traversal. Defines LBYLPattern base dataclass
    for representing detected patterns with line number and column information. Each
    concrete detector implements find_patterns() to identify specific LBYL anti-patterns.
    Uses Generic TypeVar for type-safe subclass pattern storage.

Dependencies: abc, ast, dataclasses, typing

Exports: BaseLBYLDetector, LBYLPattern

Interfaces: find_patterns(tree: ast.AST) -> list[LBYLPattern]

Implementation: Abstract base with NodeVisitor pattern for extensibility, Generic for type safety
"""

import ast
from abc import ABC
from dataclasses import dataclass
from typing import Generic, TypeVar


@dataclass
class LBYLPattern:
    """Base pattern data for detected LBYL anti-patterns."""

    line_number: int
    column: int


PatternT = TypeVar("PatternT", bound=LBYLPattern)


class BaseLBYLDetector(ast.NodeVisitor, ABC, Generic[PatternT]):
    """Base class for LBYL pattern detectors.

    Subclasses must initialize self._patterns as an empty list in __init__
    and populate it in visit methods. The _patterns attribute stores subclass-
    specific pattern types (DictKeyPattern, HasattrPattern, etc.) which all
    inherit from LBYLPattern.

    Type Parameters:
        PatternT: The specific pattern type used by this detector
    """

    _patterns: list[PatternT]

    def find_patterns(self, tree: ast.AST) -> list[LBYLPattern]:
        """Find LBYL patterns in AST.

        Args:
            tree: Python AST to analyze

        Returns:
            List of detected LBYL patterns
        """
        self._patterns = []
        self.visit(tree)
        return list(self._patterns)

"""
Purpose: Base class for LBYL pattern detectors

Scope: Abstract base providing common detector interface

Overview: Defines BaseLBYLDetector abstract class that all pattern detectors extend.
    Inherits from ast.NodeVisitor for AST traversal. Defines LBYLPattern base dataclass
    for representing detected patterns with line number and column information. Each
    concrete detector implements find_patterns() to identify specific LBYL anti-patterns.

Dependencies: abc, ast, dataclasses

Exports: BaseLBYLDetector, LBYLPattern

Interfaces: find_patterns(tree: ast.AST) -> list[LBYLPattern]

Implementation: Abstract base with NodeVisitor pattern for extensibility
"""

import ast
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class LBYLPattern:
    """Base pattern data for detected LBYL anti-patterns."""

    line_number: int
    column: int


class BaseLBYLDetector(ast.NodeVisitor, ABC):
    """Base class for LBYL pattern detectors."""

    @abstractmethod
    def find_patterns(self, tree: ast.AST) -> list[LBYLPattern]:
        """Find LBYL patterns in AST.

        Args:
            tree: Python AST to analyze

        Returns:
            List of detected LBYL patterns
        """
        raise NotImplementedError

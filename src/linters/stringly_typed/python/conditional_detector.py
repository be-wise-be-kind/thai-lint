"""
Purpose: Detect equality chain patterns in Python AST

Scope: Find 'if x == "a" elif x == "b"', or-combined, and match statement patterns

Overview: Provides ConditionalPatternDetector class that traverses Python AST to find
    equality chain patterns where strings are used instead of enums. Detects single
    equality comparisons with string constants, aggregates values from if/elif chains,
    handles or-combined comparisons, and supports Python 3.10+ match statements.
    Returns structured EqualityChainPattern dataclass instances with aggregated
    string values, pattern type, location, and optional variable name.

Dependencies: ast module for AST parsing, dataclasses for pattern structure,
    condition_extractor for comparison extraction, match_analyzer for match statements

Exports: ConditionalPatternDetector class, EqualityChainPattern dataclass

Interfaces: ConditionalPatternDetector.find_patterns(tree) -> list[EqualityChainPattern]

Implementation: AST NodeVisitor pattern with If node chain traversal and Match statement handling

Suppressions:
    - invalid-name: visit_If, visit_Match follow AST NodeVisitor method naming convention
"""

import ast
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .condition_extractor import extract_from_condition
from .constants import MIN_VALUES_FOR_PATTERN
from .match_analyzer import analyze_match_statement

if TYPE_CHECKING:
    from collections.abc import Iterator


@dataclass
class EqualityChainPattern:
    """Represents a detected equality chain pattern.

    Captures information about stringly-typed equality checks including aggregated
    string values from chains, pattern type, source location, and variable name.
    """

    string_values: set[str]
    """Set of string values aggregated from the equality chain."""

    pattern_type: str
    """Type of pattern: 'equality_chain', 'or_combined', or 'match_statement'."""

    line_number: int
    """Line number where the pattern starts (1-indexed)."""

    column: int
    """Column number where the pattern starts (0-indexed)."""

    variable_name: str | None
    """Variable name being compared, if identifiable from a simple expression."""


@dataclass
class _ChainCollector:
    """Internal collector for aggregating values from if/elif chains."""

    variable_name: str | None = None
    string_values: set[str] = field(default_factory=set)
    line_number: int = 0
    column: int = 0


class ConditionalPatternDetector(ast.NodeVisitor):
    """Detects equality chain patterns in Python AST.

    Finds patterns like 'if x == "a" elif x == "b"', or-combined comparisons,
    and match statements where strings are used instead of proper enums.
    """

    def __init__(self) -> None:
        """Initialize the detector."""
        self.patterns: list[EqualityChainPattern] = []
        self._processed_if_nodes: set[int] = set()

    def find_patterns(self, tree: ast.AST) -> list[EqualityChainPattern]:
        """Find all equality chain patterns in the AST.

        Args:
            tree: The AST to analyze

        Returns:
            List of EqualityChainPattern instances for each detected pattern
        """
        self.patterns = []
        self._processed_if_nodes = set()
        self.visit(tree)
        return self.patterns

    def visit_If(self, node: ast.If) -> None:  # pylint: disable=invalid-name
        """Visit an If node to check for equality chain patterns.

        Args:
            node: The If node to analyze
        """
        if id(node) not in self._processed_if_nodes:
            self._analyze_if_chain(node)
        self.generic_visit(node)

    def visit_Match(self, node: ast.Match) -> None:  # pylint: disable=invalid-name
        """Visit a Match node to check for string case patterns.

        Args:
            node: The Match node to analyze
        """
        pattern = analyze_match_statement(node, EqualityChainPattern)
        if pattern is not None:
            self.patterns.append(pattern)
        self.generic_visit(node)

    def _analyze_if_chain(self, node: ast.If) -> None:
        """Analyze an if/elif chain for equality patterns.

        Args:
            node: The starting If node of the chain
        """
        collector = _ChainCollector(line_number=node.lineno, column=node.col_offset)

        for if_node in self._iter_if_chain(node):
            self._processed_if_nodes.add(id(if_node))
            extract_from_condition(if_node.test, collector)

        self._emit_pattern_if_valid(collector)

    def _iter_if_chain(self, node: ast.If) -> "Iterator[ast.If]":
        """Iterate through an if/elif chain.

        Args:
            node: Starting If node

        Yields:
            Each If node in the chain including elif branches
        """
        yield node
        current: ast.If | None = node

        while current is not None:
            current = self._get_next_elif(current)
            if current is not None:
                yield current

    def _get_next_elif(self, node: ast.If) -> ast.If | None:
        """Get the next elif node in a chain.

        Args:
            node: Current If node

        Returns:
            Next elif If node, or None if no elif exists
        """
        if len(node.orelse) == 1 and isinstance(node.orelse[0], ast.If):
            return node.orelse[0]
        return None

    def _emit_pattern_if_valid(self, collector: _ChainCollector) -> None:
        """Emit a pattern if collector has sufficient values.

        Args:
            collector: Collector with aggregated values
        """
        if len(collector.string_values) < MIN_VALUES_FOR_PATTERN:
            return

        pattern = EqualityChainPattern(
            string_values=collector.string_values,
            pattern_type="equality_chain",
            line_number=collector.line_number,
            column=collector.column,
            variable_name=collector.variable_name,
        )
        self.patterns.append(pattern)

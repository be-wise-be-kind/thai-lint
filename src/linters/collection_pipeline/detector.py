"""
Purpose: AST-based detection of collection pipeline anti-patterns

Scope: Pattern matching for for loops with embedded filtering via if/continue

Overview: Implements the core detection logic for identifying imperative loop patterns
    that use if/continue for filtering instead of collection pipelines. Uses Python's
    AST module to analyze code structure and identify refactoring opportunities. Detects
    patterns like 'for x in iter: if not cond: continue; action(x)' and suggests
    refactoring to generator expressions or filter(). Handles edge cases like walrus
    operators (side effects), else branches, and empty loop bodies.

Dependencies: ast module, continue_analyzer, suggestion_builder

Exports: PipelinePatternDetector class, PatternMatch dataclass

Interfaces: PipelinePatternDetector.detect_patterns() -> list[PatternMatch]

Implementation: AST visitor pattern with delegated pattern matching and suggestion generation
"""

import ast
from dataclasses import dataclass

from . import continue_analyzer, suggestion_builder


@dataclass
class PatternMatch:
    """Represents a detected anti-pattern."""

    line_number: int
    """Line number where the for loop starts (1-indexed)."""

    loop_var: str
    """Name of the loop variable."""

    iterable: str
    """Source representation of the iterable."""

    conditions: list[str]
    """List of filter conditions (inverted from continue guards)."""

    has_side_effects: bool
    """Whether any condition has side effects."""

    suggestion: str
    """Refactoring suggestion as a code snippet."""


class PipelinePatternDetector(ast.NodeVisitor):
    """Detects for loops with embedded filtering via if/continue patterns."""

    def __init__(self, source_code: str) -> None:
        """Initialize detector with source code.

        Args:
            source_code: Python source code to analyze
        """
        self.source_code = source_code
        self.matches: list[PatternMatch] = []

    def detect_patterns(self) -> list[PatternMatch]:
        """Analyze source code and return detected patterns.

        Returns:
            List of PatternMatch objects for each detected anti-pattern
        """
        try:
            tree = ast.parse(self.source_code)
            self.visit(tree)
        except SyntaxError:
            pass  # Invalid Python, return empty list
        return self.matches

    def visit_For(self, node: ast.For) -> None:  # pylint: disable=invalid-name
        """Visit for loop and check for filtering patterns.

        Args:
            node: AST For node to analyze
        """
        match = self._analyze_for_loop(node)
        if match is not None:
            self.matches.append(match)
        self.generic_visit(node)

    def _analyze_for_loop(self, node: ast.For) -> PatternMatch | None:
        """Analyze a for loop for embedded filtering patterns.

        Args:
            node: AST For node to analyze

        Returns:
            PatternMatch if pattern detected, None otherwise
        """
        continues = continue_analyzer.extract_continue_patterns(node.body)
        if not continues:
            return None

        if continue_analyzer.has_side_effects(continues):
            return None

        if not continue_analyzer.has_body_after_continues(node.body, len(continues)):
            return None

        return self._create_match(node, continues)

    def _create_match(self, for_node: ast.For, continues: list[ast.If]) -> PatternMatch:
        """Create a PatternMatch from detected pattern.

        Args:
            for_node: AST For node
            continues: List of continue guard if statements

        Returns:
            PatternMatch object with detection information
        """
        loop_var = suggestion_builder.get_target_name(for_node.target)
        iterable = ast.unparse(for_node.iter)
        conditions = [suggestion_builder.invert_condition(c.test) for c in continues]
        suggestion = suggestion_builder.build_suggestion(loop_var, iterable, conditions)

        return PatternMatch(
            line_number=for_node.lineno,
            loop_var=loop_var,
            iterable=iterable,
            conditions=conditions,
            has_side_effects=False,
            suggestion=suggestion,
        )

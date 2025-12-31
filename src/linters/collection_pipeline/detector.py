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

Exports: PipelinePatternDetector class, PatternMatch dataclass, PatternType enum

Interfaces: PipelinePatternDetector.detect_patterns() -> list[PatternMatch]

Implementation: AST visitor pattern with delegated pattern matching and suggestion generation

Suppressions:
    - invalid-name: AST NodeVisitor visit_* methods follow convention, not PEP8
"""

import ast
from dataclasses import dataclass, field
from enum import Enum

from . import any_all_analyzer, continue_analyzer, filter_map_analyzer, suggestion_builder


class PatternType(Enum):
    """Type of collection pipeline anti-pattern detected."""

    EMBEDDED_FILTER = "embedded-filter"
    """for x: if not cond: continue; action(x) -> generator expression"""

    ANY_PATTERN = "any-pattern"
    """for x: if cond: return True; return False -> any()"""

    ALL_PATTERN = "all-pattern"
    """for x: if not cond: return False; return True -> all()"""

    FILTER_MAP = "filter-map"
    """result=[]; for x: y=f(x); if y: result.append(y) -> list comprehension"""

    TAKEWHILE = "takewhile"
    """result=[]; for x: if not cond: break; result.append(x) -> takewhile()"""


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

    pattern_type: PatternType = field(default=PatternType.EMBEDDED_FILTER)
    """Type of anti-pattern detected (default: EMBEDDED_FILTER for backward compat)."""


# Module-level pattern match factory functions (extracted from class to reduce SRP violations)


def create_any_match(match: any_all_analyzer.AnyAllMatch) -> PatternMatch:
    """Create PatternMatch for any() pattern.

    Args:
        match: AnyAllMatch from analyzer

    Returns:
        PatternMatch for the any() pattern
    """
    loop_var = suggestion_builder.get_target_name(match.for_node.target)
    iterable = ast.unparse(match.for_node.iter)
    condition = ast.unparse(match.condition)
    suggestion = suggestion_builder.build_any_suggestion(loop_var, iterable, condition)

    return PatternMatch(
        line_number=match.for_node.lineno,
        loop_var=loop_var,
        iterable=iterable,
        conditions=[condition],
        has_side_effects=False,
        suggestion=suggestion,
        pattern_type=PatternType.ANY_PATTERN,
    )


def create_all_match(match: any_all_analyzer.AnyAllMatch) -> PatternMatch:
    """Create PatternMatch for all() pattern.

    Args:
        match: AnyAllMatch from analyzer

    Returns:
        PatternMatch for the all() pattern
    """
    loop_var = suggestion_builder.get_target_name(match.for_node.target)
    iterable = ast.unparse(match.for_node.iter)
    condition = ast.unparse(match.condition)
    suggestion = suggestion_builder.build_all_suggestion(loop_var, iterable, condition)

    return PatternMatch(
        line_number=match.for_node.lineno,
        loop_var=loop_var,
        iterable=iterable,
        conditions=[condition],
        has_side_effects=False,
        suggestion=suggestion,
        pattern_type=PatternType.ALL_PATTERN,
    )


def create_filter_map_match(match: filter_map_analyzer.FilterMapMatch) -> PatternMatch:
    """Create PatternMatch for filter-map pattern.

    Args:
        match: FilterMapMatch from analyzer

    Returns:
        PatternMatch for the filter-map pattern
    """
    loop_var = suggestion_builder.get_target_name(match.for_node.target)
    iterable = ast.unparse(match.for_node.iter)
    suggestion = suggestion_builder.build_filter_map_suggestion(
        loop_var, iterable, match.transform_var, match.transform_expr
    )

    return PatternMatch(
        line_number=match.for_node.lineno,
        loop_var=loop_var,
        iterable=iterable,
        conditions=[match.transform_expr],
        has_side_effects=False,
        suggestion=suggestion,
        pattern_type=PatternType.FILTER_MAP,
    )


def create_takewhile_match(match: filter_map_analyzer.TakewhileMatch) -> PatternMatch:
    """Create PatternMatch for takewhile pattern.

    Args:
        match: TakewhileMatch from analyzer

    Returns:
        PatternMatch for the takewhile pattern
    """
    loop_var = suggestion_builder.get_target_name(match.for_node.target)
    iterable = ast.unparse(match.for_node.iter)
    condition = ast.unparse(match.condition)
    suggestion = suggestion_builder.build_takewhile_suggestion(loop_var, iterable, condition)

    return PatternMatch(
        line_number=match.for_node.lineno,
        loop_var=loop_var,
        iterable=iterable,
        conditions=[condition],
        has_side_effects=False,
        suggestion=suggestion,
        pattern_type=PatternType.TAKEWHILE,
    )


def create_embedded_filter_match(for_node: ast.For, continues: list[ast.If]) -> PatternMatch:
    """Create a PatternMatch for embedded filter pattern.

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
        pattern_type=PatternType.EMBEDDED_FILTER,
    )


def analyze_for_loop(node: ast.For) -> PatternMatch | None:
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

    return create_embedded_filter_match(node, continues)


class PipelinePatternDetector(ast.NodeVisitor):
    """Detects for loops with embedded filtering via if/continue patterns."""

    def __init__(self, source_code: str) -> None:
        """Initialize detector with source code.

        Args:
            source_code: Python source code to analyze
        """
        self.source_code = source_code
        self.matches: list[PatternMatch] = []
        self._func_body_stack: list[list[ast.stmt]] = []

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

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:  # pylint: disable=invalid-name
        """Visit function and track body for any/all pattern detection.

        Args:
            node: AST FunctionDef node
        """
        self._func_body_stack.append(node.body)
        self.generic_visit(node)
        self._func_body_stack.pop()

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:  # pylint: disable=invalid-name
        """Visit async function and track body for any/all pattern detection.

        Args:
            node: AST AsyncFunctionDef node
        """
        self._func_body_stack.append(node.body)
        self.generic_visit(node)
        self._func_body_stack.pop()

    def visit_For(self, node: ast.For) -> None:  # pylint: disable=invalid-name
        """Visit for loop and check for filtering patterns.

        Args:
            node: AST For node to analyze
        """
        match = self._find_pattern_match(node)
        if match is not None:
            self.matches.append(match)
        self.generic_visit(node)

    def _find_pattern_match(self, node: ast.For) -> PatternMatch | None:
        """Find the first matching anti-pattern for a for loop.

        Checks patterns in priority order: any/all, filter-map/takewhile, embedded filter.

        Args:
            node: AST For node to analyze

        Returns:
            PatternMatch if any pattern detected, None otherwise
        """
        # Check for any/all patterns (requires function context)
        any_all_match = self._analyze_any_all_pattern(node)
        if any_all_match is not None:
            return any_all_match

        # Check for filter-map/takewhile patterns
        filter_map_match = self._analyze_filter_map_pattern(node)
        if filter_map_match is not None:
            return filter_map_match

        # Check for embedded filter patterns
        return analyze_for_loop(node)

    def _analyze_any_all_pattern(self, node: ast.For) -> PatternMatch | None:
        """Analyze a for loop for any()/all() patterns.

        Args:
            node: AST For node to analyze

        Returns:
            PatternMatch if any/all pattern detected, None otherwise
        """
        if not self._func_body_stack:
            return None

        func_body = self._func_body_stack[-1]

        # Try any() pattern first
        any_match = any_all_analyzer.extract_any_pattern(func_body, node)
        if any_match is not None:
            return create_any_match(any_match)

        # Try all() pattern
        all_match = any_all_analyzer.extract_all_pattern(func_body, node)
        if all_match is not None:
            return create_all_match(all_match)

        return None

    def _analyze_filter_map_pattern(self, node: ast.For) -> PatternMatch | None:
        """Analyze a for loop for filter-map/takewhile patterns.

        Args:
            node: AST For node to analyze

        Returns:
            PatternMatch if filter-map/takewhile pattern detected, None otherwise
        """
        if not self._func_body_stack:
            return None

        func_body = self._func_body_stack[-1]

        # Try filter-map pattern first
        fm_match = filter_map_analyzer.extract_filter_map_pattern(func_body, node)
        if fm_match is not None:
            return create_filter_map_match(fm_match)

        # Try takewhile pattern
        tw_match = filter_map_analyzer.extract_takewhile_pattern(func_body, node)
        if tw_match is not None:
            return create_takewhile_match(tw_match)

        return None

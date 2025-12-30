"""
Purpose: Analyze Python match statements for stringly-typed patterns

Scope: Extract string values from match statement cases

Overview: Provides MatchStatementAnalyzer class that analyzes Python 3.10+ match
    statements to detect stringly-typed patterns. Extracts string values from
    case patterns and returns structured results. Separated from main detector
    to maintain single responsibility and reduce class complexity.

Dependencies: ast module, constants module, variable_extractor

Exports: MatchStatementAnalyzer class

Interfaces: MatchStatementAnalyzer.analyze(node) -> EqualityChainPattern | None

Implementation: AST pattern matching for MatchValue nodes with string constants
"""

from __future__ import annotations

import ast
from typing import TYPE_CHECKING

from .constants import MIN_VALUES_FOR_PATTERN
from .variable_extractor import extract_variable_name

if TYPE_CHECKING:
    from .conditional_detector import EqualityChainPattern


def analyze_match_statement(
    node: ast.Match,
    pattern_class: type[EqualityChainPattern],
) -> EqualityChainPattern | None:
    """Analyze a match statement for string case patterns.

    Args:
        node: Match statement node to analyze
        pattern_class: The EqualityChainPattern class to use for results

    Returns:
        Pattern instance if valid match found, None otherwise
    """
    string_values = _collect_string_cases(node.cases)

    if len(string_values) < MIN_VALUES_FOR_PATTERN:
        return None

    var_name = extract_variable_name(node.subject)
    return pattern_class(
        string_values=string_values,
        pattern_type="match_statement",
        line_number=node.lineno,
        column=node.col_offset,
        variable_name=var_name,
    )


def _collect_string_cases(cases: list[ast.match_case]) -> set[str]:
    """Collect string values from match cases.

    Args:
        cases: List of match_case nodes

    Returns:
        Set of string values from MatchValue patterns
    """
    string_values: set[str] = set()

    for case in cases:
        value = _extract_case_string_value(case.pattern)
        if value is not None:
            string_values.add(value)

    return string_values


def _extract_case_string_value(pattern: ast.pattern) -> str | None:
    """Extract string value from a case pattern.

    Args:
        pattern: Match case pattern node

    Returns:
        String value if pattern is a MatchValue with string, None otherwise
    """
    if not isinstance(pattern, ast.MatchValue):
        return None
    if not isinstance(pattern.value, ast.Constant):
        return None
    if not isinstance(pattern.value.value, str):
        return None
    return pattern.value.value

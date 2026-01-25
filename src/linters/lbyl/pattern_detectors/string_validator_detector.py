"""
Purpose: AST-based detector for string validator LBYL patterns

Scope: Detects 'if s.isnumeric(): int(s)' patterns in Python code

Overview: Provides StringValidatorDetector class that uses AST traversal to find LBYL
    anti-patterns involving string validation before conversion. Identifies patterns where
    code checks string content (isnumeric, isdigit, isdecimal) before calling conversion
    functions (int, float). Returns StringValidatorPattern objects containing the string
    name, validator method, conversion function, and location.

Dependencies: ast module, base detector classes from pattern_detectors.base

Exports: StringValidatorPattern, StringValidatorDetector

Interfaces: StringValidatorDetector.find_patterns(tree: ast.AST) -> list[StringValidatorPattern]

Implementation: AST NodeVisitor pattern with visit_If to detect string validation followed
    by conversion call

Suppressions:
    - N802: visit_If follows Python AST visitor naming convention (camelCase required)
    - invalid-name: visit_If follows Python AST visitor naming convention (camelCase required)
"""

import ast
from collections.abc import Iterator
from dataclasses import dataclass

from .base import BaseLBYLDetector, LBYLPattern

# Validator methods that check numeric content
NUMERIC_VALIDATORS = frozenset({"isnumeric", "isdigit", "isdecimal"})

# Conversion functions that convert strings to numbers
NUMERIC_CONVERSIONS = frozenset({"int", "float"})


@dataclass
class StringValidatorPattern(LBYLPattern):
    """Pattern data for string validator LBYL anti-pattern."""

    string_name: str
    validator_method: str
    conversion_func: str


def _try_extract_validator_call(node: ast.expr) -> tuple[ast.expr | None, str | None]:
    """Try to extract string validator call.

    Returns:
        Tuple of (string_expr, validator_method) or (None, None) if not valid.
    """
    if not isinstance(node, ast.Call):
        return None, None
    if not isinstance(node.func, ast.Attribute):
        return None, None
    if node.func.attr not in NUMERIC_VALIDATORS:
        return None, None
    return node.func.value, node.func.attr


def _get_string_expression_key(expr: ast.expr) -> str:
    """Get a normalized key for comparing string expressions."""
    return ast.dump(expr)


def _get_conversion_func_name(node: ast.AST) -> str | None:
    """Get conversion function name if node is a numeric conversion call."""
    if not isinstance(node, ast.Call):
        return None
    if not isinstance(node.func, ast.Name):
        return None
    if node.func.id not in NUMERIC_CONVERSIONS:
        return None
    return node.func.id


def _iter_ast_nodes(body: list[ast.stmt]) -> Iterator[ast.AST]:
    """Iterate over all AST nodes in a list of statements."""
    for stmt in body:
        yield from ast.walk(stmt)


def _is_matching_call(node: ast.AST, expected_key: str) -> str | None:
    """Check if node is a matching conversion call."""
    if not isinstance(node, ast.Call):
        return None
    func_name = _get_conversion_func_name(node)
    if func_name and node.args and ast.dump(node.args[0]) == expected_key:
        return func_name
    return None


def _find_conversion(body: list[ast.stmt], expected_key: str) -> str | None:
    """Find first matching conversion in body."""
    for node in _iter_ast_nodes(body):
        result = _is_matching_call(node, expected_key)
        if result:
            return result
    return None


class StringValidatorDetector(BaseLBYLDetector[StringValidatorPattern]):
    """Detects 'if s.isnumeric(): int(s)' LBYL patterns."""

    def __init__(self) -> None:
        """Initialize the detector."""
        self._patterns: list[StringValidatorPattern] = []

    def visit_If(self, node: ast.If) -> None:  # noqa: N802  # pylint: disable=invalid-name
        """Visit if statement to check for string validator LBYL pattern.

        Args:
            node: AST If node to analyze
        """
        self._check_validator_pattern(node)
        self.generic_visit(node)

    def _check_validator_pattern(self, node: ast.If) -> None:
        """Check if node is a string validator LBYL pattern and record it."""
        string_expr, validator = _try_extract_validator_call(node.test)
        if string_expr is None or validator is None:
            return

        expected_key = _get_string_expression_key(string_expr)
        conversion = _find_conversion(node.body, expected_key)
        if conversion:
            self._patterns.append(self._create_pattern(node, string_expr, validator, conversion))

    def _create_pattern(
        self,
        node: ast.If,
        string_expr: ast.expr,
        validator: str,
        conversion: str,
    ) -> StringValidatorPattern:
        """Create StringValidatorPattern from detected pattern."""
        return StringValidatorPattern(
            line_number=node.lineno,
            column=node.col_offset,
            string_name=ast.unparse(string_expr),
            validator_method=validator,
            conversion_func=conversion,
        )

"""
Purpose: AST-based detector for None check LBYL patterns

Scope: Detects 'if x is not None: x.method()' patterns in Python code

Overview: Provides NoneCheckDetector class that uses AST traversal to find LBYL anti-patterns
    involving None checking. Identifies patterns where code checks if a variable is not None
    before using it (e.g., 'if x is not None: x.method()'). Also detects inverse patterns
    with else branches. Returns NoneCheckPattern objects containing the variable name and
    location. Avoids false positives for different variables, walrus operator assignments.

Dependencies: ast module, base detector classes from pattern_detectors.base

Exports: NoneCheckPattern, NoneCheckDetector

Interfaces: NoneCheckDetector.find_patterns(tree: ast.AST) -> list[NoneCheckPattern]

Implementation: AST NodeVisitor pattern with visit_If to detect None comparison followed by
    variable usage

Suppressions:
    - N802: visit_If follows Python AST visitor naming convention (camelCase required)
    - invalid-name: visit_If follows Python AST visitor naming convention (camelCase required)
"""

import ast
from dataclasses import dataclass

from .base import BaseLBYLDetector, LBYLPattern


@dataclass
class NoneCheckPattern(LBYLPattern):
    """Pattern data for None check LBYL anti-pattern."""

    variable_name: str


def _try_extract_none_check(node: ast.expr) -> tuple[ast.expr | None, bool]:
    """Try to extract variable from None comparison.

    Returns:
        Tuple of (variable_expr, is_not_none_check) or (None, False) if not valid.
        is_not_none_check is True for 'is not None', False for 'is None'.
    """
    if not isinstance(node, ast.Compare):
        return None, False
    if len(node.ops) != 1 or len(node.comparators) != 1:
        return None, False
    return _extract_none_comparison(node)


def _is_none_constant(node: ast.expr) -> bool:
    """Check if node is a None constant."""
    return isinstance(node, ast.Constant) and node.value is None


def _extract_var_from_none_check(var_side: ast.expr, op: ast.cmpop) -> tuple[ast.expr | None, bool]:
    """Extract variable from None comparison if valid."""
    if _is_walrus_expression(var_side):
        return None, False
    return var_side, isinstance(op, ast.IsNot)


def _extract_none_comparison(node: ast.Compare) -> tuple[ast.expr | None, bool]:
    """Extract variable from 'x is None' or 'x is not None' comparison.

    Returns:
        Tuple of (variable_expr, is_not_none) or (None, False) if not valid.
    """
    op = node.ops[0]
    if not isinstance(op, (ast.Is, ast.IsNot)):
        return None, False

    left, right = node.left, node.comparators[0]

    # Check for 'x is None', 'x is not None'
    if _is_none_constant(right):
        return _extract_var_from_none_check(left, op)
    # Check for 'None is x', 'None is not x'
    if _is_none_constant(left):
        return _extract_var_from_none_check(right, op)

    return None, False


def _is_walrus_expression(node: ast.expr) -> bool:
    """Check if expression contains walrus operator (assignment expression)."""
    return isinstance(node, ast.NamedExpr)


class NoneCheckDetector(BaseLBYLDetector[NoneCheckPattern]):
    """Detects 'if x is not None: x.method()' LBYL patterns."""

    def __init__(self) -> None:
        """Initialize the detector."""
        self._patterns: list[NoneCheckPattern] = []

    def visit_If(self, node: ast.If) -> None:  # noqa: N802  # pylint: disable=invalid-name
        """Visit if statement to check for None check LBYL pattern.

        Args:
            node: AST If node to analyze
        """
        self._check_none_pattern(node)
        self.generic_visit(node)

    def _check_none_pattern(self, node: ast.If) -> None:
        """Check if node is a None check LBYL pattern and record it."""
        var_expr, is_not_none = _try_extract_none_check(node.test)
        if var_expr is None:
            return

        # For 'is not None', check body for variable usage
        # For 'is None', check else branch for variable usage
        body_to_check = node.body if is_not_none else node.orelse
        if not body_to_check:
            return

        if self._body_has_variable_usage(body_to_check, var_expr):
            self._patterns.append(self._create_pattern(node, var_expr))

    def _body_has_variable_usage(self, body: list[ast.stmt], var_expr: ast.expr) -> bool:
        """Check if body contains usage of the None-checked variable."""
        expected_var = ast.dump(var_expr)
        return any(
            self._is_variable_usage(node, expected_var) for stmt in body for node in ast.walk(stmt)
        )

    def _is_variable_usage(self, node: ast.AST, expected_var: str) -> bool:
        """Check if node represents usage of the expected variable."""
        if isinstance(node, ast.Attribute):
            return ast.dump(node.value) == expected_var
        if isinstance(node, ast.Subscript):
            return ast.dump(node.value) == expected_var
        if isinstance(node, ast.Call):
            return ast.dump(node.func) == expected_var
        return False

    def _create_pattern(self, node: ast.If, var_expr: ast.expr) -> NoneCheckPattern:
        """Create NoneCheckPattern from detected pattern."""
        return NoneCheckPattern(
            line_number=node.lineno,
            column=node.col_offset,
            variable_name=ast.unparse(var_expr),
        )

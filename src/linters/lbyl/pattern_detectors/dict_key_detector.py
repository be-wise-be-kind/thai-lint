"""
Purpose: AST-based detector for dict key LBYL patterns

Scope: Detects 'if key in dict: dict[key]' patterns in Python code

Overview: Provides DictKeyDetector class that uses AST traversal to find LBYL anti-patterns
    involving dict key checking. Identifies patterns where code checks if a key exists in a
    dict before accessing it (e.g., 'if key in d: d[key]'). Returns DictKeyPattern objects
    containing the dict name, key expression, and location. Avoids false positives for
    different dict/key combinations, walrus operator patterns, and dict.get() usage.

Dependencies: ast module, base detector classes from pattern_detectors.base

Exports: DictKeyPattern, DictKeyDetector

Interfaces: DictKeyDetector.find_patterns(tree: ast.AST) -> list[DictKeyPattern]

Implementation: AST NodeVisitor pattern with visit_If to detect in-check followed by subscript

Suppressions:
    - N802: visit_If follows Python AST visitor naming convention (camelCase required)
    - invalid-name: visit_If follows Python AST visitor naming convention (camelCase required)
"""

import ast
from dataclasses import dataclass

from .base import BaseLBYLDetector, LBYLPattern


@dataclass
class DictKeyPattern(LBYLPattern):
    """Pattern data for dict key LBYL anti-pattern."""

    dict_name: str
    key_expression: str


def _is_walrus_get_pattern(test: ast.Compare) -> bool:
    """Check if test is '(val := d.get(k)) is not None' pattern."""
    if not isinstance(test.left, ast.NamedExpr):
        return False
    if not isinstance(test.left.value, ast.Call):
        return False
    call = test.left.value
    return isinstance(call.func, ast.Attribute) and call.func.attr == "get"


def _is_simple_in_compare(test: ast.Compare) -> bool:
    """Check if Compare has single In operator and one comparator."""
    return len(test.ops) == 1 and isinstance(test.ops[0], ast.In) and len(test.comparators) == 1


def _extract_in_check(test: ast.expr) -> tuple[ast.expr | None, ast.expr | None]:
    """Extract dict and key from 'key in dict' comparison."""
    if isinstance(test, ast.NamedExpr):
        return None, None
    if not isinstance(test, ast.Compare):
        return None, None
    if not _is_simple_in_compare(test) or _is_walrus_get_pattern(test):
        return None, None
    return test.comparators[0], test.left


class DictKeyDetector(BaseLBYLDetector):
    """Detects 'if key in dict: dict[key]' LBYL patterns."""

    def __init__(self) -> None:
        """Initialize the detector."""
        self._patterns: list[DictKeyPattern] = []

    def find_patterns(self, tree: ast.AST) -> list[LBYLPattern]:
        """Find dict key LBYL patterns in AST.

        Args:
            tree: Python AST to analyze

        Returns:
            List of detected DictKeyPattern objects
        """
        self._patterns = []
        self.visit(tree)
        return list(self._patterns)

    def visit_If(self, node: ast.If) -> None:  # noqa: N802  # pylint: disable=invalid-name
        """Visit if statement to check for dict key LBYL pattern.

        Args:
            node: AST If node to analyze
        """
        dict_expr, key_expr = _extract_in_check(node.test)

        if dict_expr is not None and key_expr is not None:
            if self._body_has_subscript_match(node.body, dict_expr, key_expr):
                self._patterns.append(self._create_pattern(node, dict_expr, key_expr))

        self.generic_visit(node)

    def _body_has_subscript_match(
        self, body: list[ast.stmt], dict_expr: ast.expr, key_expr: ast.expr
    ) -> bool:
        """Check if body contains dict[key] access matching the in-check."""
        expected = (ast.dump(dict_expr), ast.dump(key_expr))
        return any(
            (ast.dump(node.value), ast.dump(node.slice)) == expected
            for stmt in body
            for node in ast.walk(stmt)
            if isinstance(node, ast.Subscript)
        )

    def _create_pattern(
        self, node: ast.If, dict_expr: ast.expr, key_expr: ast.expr
    ) -> DictKeyPattern:
        """Create DictKeyPattern from detected pattern."""
        return DictKeyPattern(
            line_number=node.lineno,
            column=node.col_offset,
            dict_name=ast.unparse(dict_expr),
            key_expression=ast.unparse(key_expr),
        )

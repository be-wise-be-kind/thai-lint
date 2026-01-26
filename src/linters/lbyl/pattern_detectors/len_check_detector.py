"""
Purpose: AST-based detector for len check LBYL patterns

Scope: Detects 'if len(lst) > i: lst[i]' patterns in Python code

Overview: Provides LenCheckDetector class that uses AST traversal to find LBYL anti-patterns
    involving length checking before index access. Identifies patterns where code checks if
    a collection's length is sufficient before accessing an element by index. Handles various
    comparison operators (>, >=, <, <=) and operand orderings. Returns LenCheckPattern objects
    containing the collection name, index expression, and location. Avoids false positives
    for different collection/index combinations.

Dependencies: ast module, base detector classes from pattern_detectors.base

Exports: LenCheckPattern, LenCheckDetector

Interfaces: LenCheckDetector.find_patterns(tree: ast.AST) -> list[LenCheckPattern]

Implementation: AST NodeVisitor pattern with visit_If to detect len check followed by
    subscript access

Suppressions:
    - N802: visit_If follows Python AST visitor naming convention (camelCase required)
    - invalid-name: visit_If follows Python AST visitor naming convention (camelCase required)
"""

import ast
from dataclasses import dataclass

from .base import BaseLBYLDetector, LBYLPattern


@dataclass
class LenCheckPattern(LBYLPattern):
    """Pattern data for len check LBYL anti-pattern."""

    collection_name: str
    index_expression: str


def _extract_len_call_collection(node: ast.expr) -> ast.expr | None:
    """Extract collection from len(collection) call, or None if not len call."""
    if not isinstance(node, ast.Call):
        return None
    if not isinstance(node.func, ast.Name) or node.func.id != "len":
        return None
    if len(node.args) != 1:
        return None
    return node.args[0]


def _extract_len_from_binop(node: ast.expr) -> ast.expr | None:
    """Extract collection from len(lst) - 1 or similar BinOp."""
    if isinstance(node, ast.BinOp):
        # len(lst) - 1 or 1 + len(lst)
        collection = _extract_len_call_collection(node.left)
        if collection is not None:
            return collection
        return _extract_len_call_collection(node.right)
    return _extract_len_call_collection(node)


def _is_valid_compare(test: ast.expr) -> bool:
    """Check if test is a simple comparison with one operator."""
    if not isinstance(test, ast.Compare):
        return False
    return len(test.ops) == 1 and len(test.comparators) == 1


def _is_unary_constant(node: ast.expr) -> bool:
    """Check if node is unary minus on constant (e.g., -1)."""
    return isinstance(node, ast.UnaryOp) and isinstance(node.operand, ast.Constant)


def _is_constant_index(node: ast.expr) -> bool:
    """Check if node is a constant (literal number or simple expression).

    We don't flag len checks with constant indices as LBYL because they're
    typically local validation patterns (e.g., if len(lst) >= 2: lst[0], lst[1])
    rather than race-condition-prone LBYL anti-patterns.
    """
    if isinstance(node, ast.Constant) or _is_unary_constant(node):
        return True
    if isinstance(node, ast.BinOp):
        return _is_constant_index(node.left) and _is_constant_index(node.right)
    return False


def _check_len_greater_than(
    op: ast.cmpop, left: ast.expr, right: ast.expr
) -> tuple[ast.expr | None, ast.expr | None]:
    """Check for len(lst) > i or len(lst) >= i pattern."""
    if not isinstance(op, (ast.Gt, ast.GtE)):
        return None, None
    collection = _extract_len_from_binop(left)
    if collection is not None:
        return collection, right
    return None, None


def _check_index_less_than(
    op: ast.cmpop, left: ast.expr, right: ast.expr
) -> tuple[ast.expr | None, ast.expr | None]:
    """Check for i < len(lst) or i <= len(lst) pattern."""
    if not isinstance(op, (ast.Lt, ast.LtE)):
        return None, None
    collection = _extract_len_from_binop(right)
    if collection is not None:
        return collection, left
    return None, None


def _extract_len_check(test: ast.expr) -> tuple[ast.expr | None, ast.expr | None]:
    """Extract (collection, index) from len comparison, or (None, None)."""
    if not isinstance(test, ast.Compare):
        return None, None
    if not _is_valid_compare(test):
        return None, None

    op = test.ops[0]
    left = test.left
    right = test.comparators[0]

    result = _check_len_greater_than(op, left, right)
    if result[0] is not None:
        return result
    return _check_index_less_than(op, left, right)


class LenCheckDetector(BaseLBYLDetector[LenCheckPattern]):
    """Detects 'if len(lst) > i: lst[i]' LBYL patterns."""

    def __init__(self) -> None:
        """Initialize the detector."""
        self._patterns: list[LenCheckPattern] = []

    def visit_If(self, node: ast.If) -> None:  # noqa: N802  # pylint: disable=invalid-name
        """Visit if statement to check for len check LBYL pattern."""
        self._check_len_pattern(node)
        self.generic_visit(node)

    def _check_len_pattern(self, node: ast.If) -> None:
        """Check if node matches len check LBYL pattern."""
        collection_expr, index_expr = _extract_len_check(node.test)
        if collection_expr is None or index_expr is None:
            return

        # Skip constant index checks - they're local validation, not LBYL
        if _is_constant_index(index_expr):
            return

        if self._body_has_subscript_match(node.body, collection_expr):
            self._patterns.append(self._create_pattern(node, collection_expr, index_expr))

    def _body_has_subscript_match(self, body: list[ast.stmt], collection_expr: ast.expr) -> bool:
        """Check if body contains collection[index] access matching the len check."""
        expected_collection = ast.dump(collection_expr)
        return any(
            isinstance(node, ast.Subscript) and ast.dump(node.value) == expected_collection
            for stmt in body
            for node in ast.walk(stmt)
        )

    def _create_pattern(
        self, node: ast.If, collection_expr: ast.expr, index_expr: ast.expr
    ) -> LenCheckPattern:
        """Create LenCheckPattern from detected pattern."""
        return LenCheckPattern(
            line_number=node.lineno,
            column=node.col_offset,
            collection_name=ast.unparse(collection_expr),
            index_expression=ast.unparse(index_expr),
        )

"""
Purpose: AST-based detector for division zero-check LBYL patterns

Scope: Detects 'if x != 0: a / x' patterns in Python code

Overview: Provides DivisionCheckDetector class that uses AST traversal to find LBYL
    anti-patterns involving zero-checks before division. Identifies patterns where code
    checks if a divisor is non-zero before dividing (e.g., 'if x != 0: a / x'). Also
    detects inverse patterns with else branches and truthy checks. Covers division (/),
    integer division (//), modulo (%), and augmented operators (/=, //=, %=).

Dependencies: ast module, base detector classes from pattern_detectors.base

Exports: DivisionCheckPattern, DivisionCheckDetector

Interfaces: DivisionCheckDetector.find_patterns(tree: ast.AST) -> list[DivisionCheckPattern]

Implementation: AST NodeVisitor pattern with visit_If to detect zero comparison followed
    by division using the checked variable

Suppressions:
    - N802: visit_If follows Python AST visitor naming convention (camelCase required)
    - invalid-name: visit_If follows Python AST visitor naming convention (camelCase required)
"""

import ast
from collections.abc import Iterator
from dataclasses import dataclass

from .base import BaseLBYLDetector, LBYLPattern


@dataclass
class DivisionCheckPattern(LBYLPattern):
    """Pattern data for division check LBYL anti-pattern."""

    divisor_name: str
    operation: str


def _is_zero_constant(node: ast.expr) -> bool:
    """Check if node is a zero constant."""
    return isinstance(node, ast.Constant) and node.value == 0


def _try_extract_zero_check(node: ast.expr) -> tuple[ast.expr | None, bool]:
    """Try to extract variable from zero comparison.

    Returns:
        Tuple of (variable_expr, is_non_zero_check) or (None, False) if not valid.
        is_non_zero_check is True for '!= 0', False for '== 0'.
    """
    if isinstance(node, ast.Compare):
        return _extract_zero_comparison(node)
    # Handle truthy check: if x: (implicit != 0)
    if isinstance(node, ast.Name):
        return node, True
    if isinstance(node, ast.Attribute):
        return node, True
    if isinstance(node, ast.Subscript):
        return node, True
    return None, False


def _is_equality_op(node: ast.Compare) -> ast.cmpop | None:
    """Return equality operator if it's a single eq/noteq comparison, else None."""
    if len(node.ops) != 1 or len(node.comparators) != 1:
        return None
    op = node.ops[0]
    return op if isinstance(op, (ast.Eq, ast.NotEq)) else None


def _extract_zero_comparison(node: ast.Compare) -> tuple[ast.expr | None, bool]:
    """Extract variable from 'x != 0' or 'x == 0' comparison.

    Returns:
        Tuple of (variable_expr, is_non_zero) or (None, False) if not valid.
    """
    op = _is_equality_op(node)
    if op is None:
        return None, False

    left, right = node.left, node.comparators[0]
    is_not_eq = isinstance(op, ast.NotEq)

    # Check for 'x != 0', 'x == 0', '0 != x', '0 == x'
    if _is_zero_constant(right):
        return left, is_not_eq
    if _is_zero_constant(left):
        return right, is_not_eq

    return None, False


def _get_expression_key(expr: ast.expr) -> str:
    """Get a normalized key for comparing expressions."""
    return ast.dump(expr)


# Maps BinOp operator types to their string representation
DIVISION_BINOP_MAP = {
    ast.Div: "/",
    ast.FloorDiv: "//",
    ast.Mod: "%",
}

# Maps AugAssign operator types to their string representation
DIVISION_AUGOP_MAP = {
    ast.Div: "/=",
    ast.FloorDiv: "//=",
    ast.Mod: "%=",
}

# Keywords suggesting path-related variables (likely pathlib, not numeric division)
PATH_KEYWORDS = frozenset({"path", "file", "dir", "folder", "root", "name", "directory"})


def _get_variable_name(expr: ast.expr) -> str:
    """Extract variable name from expression for heuristic checks."""
    if isinstance(expr, ast.Name):
        return expr.id.lower()
    if isinstance(expr, ast.Attribute):
        return expr.attr.lower()
    return ""


def _looks_like_path_variable(expr: ast.expr) -> bool:
    """Check if expression name suggests it's a path-related variable."""
    name = _get_variable_name(expr)
    return any(keyword in name for keyword in PATH_KEYWORDS)


def _is_likely_pathlib_division(node: ast.BinOp) -> bool:
    """Check if BinOp is likely pathlib path joining, not numeric division.

    Heuristics:
    - If left operand has path-related name (e.g., project_root, base_path)
    - If right operand has path-related name (e.g., file_name, sub_dir)
    - Only applies to single `/`, not `//` or `%`
    """
    if not isinstance(node.op, ast.Div):
        return False
    return _looks_like_path_variable(node.left) or _looks_like_path_variable(node.right)


def _check_binop(node: ast.BinOp, expected_key: str) -> str | None:
    """Check if BinOp is division with expected divisor."""
    op_str = DIVISION_BINOP_MAP.get(type(node.op))
    if not op_str:
        return None
    if _get_expression_key(node.right) != expected_key:
        return None
    # Skip likely pathlib operations (false positive avoidance)
    if _is_likely_pathlib_division(node):
        return None
    return op_str


def _check_augassign(node: ast.AugAssign, expected_key: str) -> str | None:
    """Check if AugAssign is division with expected divisor."""
    op_str = DIVISION_AUGOP_MAP.get(type(node.op))
    if op_str and _get_expression_key(node.value) == expected_key:
        return op_str
    return None


def _iter_ast_nodes(body: list[ast.stmt]) -> Iterator[ast.AST]:
    """Iterate over all AST nodes in a list of statements."""
    for stmt in body:
        yield from ast.walk(stmt)


def _check_division_node(node: ast.AST, expected_key: str) -> str | None:
    """Check if AST node is a division using expected divisor."""
    if isinstance(node, ast.BinOp):
        return _check_binop(node, expected_key)
    if isinstance(node, ast.AugAssign):
        return _check_augassign(node, expected_key)
    return None


def _find_division(body: list[ast.stmt], expected_key: str) -> str | None:
    """Find first division operation using expected divisor in body."""
    for node in _iter_ast_nodes(body):
        result = _check_division_node(node, expected_key)
        if result:
            return result
    return None


class DivisionCheckDetector(BaseLBYLDetector[DivisionCheckPattern]):
    """Detects 'if x != 0: a / x' LBYL patterns."""

    def __init__(self) -> None:
        """Initialize the detector."""
        self._patterns: list[DivisionCheckPattern] = []

    def visit_If(self, node: ast.If) -> None:  # noqa: N802  # pylint: disable=invalid-name
        """Visit if statement to check for division zero-check LBYL pattern.

        Args:
            node: AST If node to analyze
        """
        self._check_division_pattern(node)
        self.generic_visit(node)

    def _check_division_pattern(self, node: ast.If) -> None:
        """Check if node is a division zero-check LBYL pattern and record it."""
        var_expr, is_non_zero = _try_extract_zero_check(node.test)
        if var_expr is None:
            return

        # For '!= 0' or truthy, check body; for '== 0', check else branch
        body_to_check = node.body if is_non_zero else node.orelse
        if not body_to_check:
            return

        expected_key = _get_expression_key(var_expr)
        operation = _find_division(body_to_check, expected_key)
        if operation:
            self._patterns.append(self._create_pattern(node, var_expr, operation))

    def _create_pattern(
        self, node: ast.If, var_expr: ast.expr, operation: str
    ) -> DivisionCheckPattern:
        """Create DivisionCheckPattern from detected pattern."""
        return DivisionCheckPattern(
            line_number=node.lineno,
            column=node.col_offset,
            divisor_name=ast.unparse(var_expr),
            operation=operation,
        )

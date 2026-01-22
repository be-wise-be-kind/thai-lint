"""
Purpose: AST-based detector for isinstance LBYL patterns

Scope: Detects 'if isinstance(x, Type): x.method()' patterns in Python code

Overview: Provides IsinstanceDetector class that uses AST traversal to find LBYL anti-patterns
    involving isinstance checking. Identifies patterns where code checks if an object is an
    instance of a type before performing type-specific operations. Returns IsinstancePattern
    objects containing the object name, type name, and location. This detector is disabled by
    default in config because many isinstance checks are valid type narrowing.

Dependencies: ast module, base detector classes from pattern_detectors.base

Exports: IsinstancePattern, IsinstanceDetector

Interfaces: IsinstanceDetector.find_patterns(tree: ast.AST) -> list[IsinstancePattern]

Implementation: AST NodeVisitor pattern with visit_If to detect isinstance check followed by
    operations on the checked object

Suppressions:
    - N802: visit_If follows Python AST visitor naming convention (camelCase required)
    - invalid-name: visit_If follows Python AST visitor naming convention (camelCase required)
"""

import ast
from dataclasses import dataclass

from .base import BaseLBYLDetector, LBYLPattern


@dataclass
class IsinstancePattern(LBYLPattern):
    """Pattern data for isinstance LBYL anti-pattern."""

    object_name: str
    type_name: str


def _try_extract_isinstance_call(node: ast.expr) -> tuple[ast.expr | None, str | None]:
    """Try to extract isinstance call arguments.

    Returns:
        Tuple of (object_expr, type_name) or (None, None) if not a valid isinstance call.
    """
    if not isinstance(node, ast.Call):
        return None, None
    if not isinstance(node.func, ast.Name) or node.func.id != "isinstance":
        return None, None
    return _extract_isinstance_args(node)


def _extract_isinstance_args(call: ast.Call) -> tuple[ast.expr | None, str | None]:
    """Extract object and type name from isinstance call args.

    Returns:
        Tuple of (object_expr, type_name_str) or (None, None) if not valid.
    """
    if len(call.args) != 2:
        return None, None
    return call.args[0], ast.unparse(call.args[1])


class IsinstanceDetector(BaseLBYLDetector[IsinstancePattern]):
    """Detects 'if isinstance(x, Type): x.method()' LBYL patterns."""

    def __init__(self) -> None:
        """Initialize the detector."""
        self._patterns: list[IsinstancePattern] = []

    def visit_If(self, node: ast.If) -> None:  # noqa: N802  # pylint: disable=invalid-name
        """Visit if statement to check for isinstance LBYL pattern.

        Args:
            node: AST If node to analyze
        """
        self._check_isinstance_pattern(node)
        self.generic_visit(node)

    def _check_isinstance_pattern(self, node: ast.If) -> None:
        """Check if node is an isinstance LBYL pattern and record it."""
        obj_expr, type_name = _try_extract_isinstance_call(node.test)
        if obj_expr is None or type_name is None:
            return

        if self._body_has_object_operation(node.body, obj_expr):
            self._patterns.append(self._create_pattern(node, obj_expr, type_name))

    def _body_has_object_operation(self, body: list[ast.stmt], obj_expr: ast.expr) -> bool:
        """Check if body contains operations on the isinstance-checked object."""
        expected_obj = ast.dump(obj_expr)
        return any(
            self._node_uses_object(node, expected_obj) for stmt in body for node in ast.walk(stmt)
        )

    def _node_uses_object(self, node: ast.AST, expected_obj: str) -> bool:
        """Check if AST node uses the expected object."""
        if isinstance(node, ast.Attribute):
            return ast.dump(node.value) == expected_obj
        if isinstance(node, ast.Subscript):
            return ast.dump(node.value) == expected_obj
        if isinstance(node, ast.BinOp):
            return self._binop_uses_object(node, expected_obj)
        return False

    def _binop_uses_object(self, node: ast.BinOp, expected_obj: str) -> bool:
        """Check if binary operation uses the checked object."""
        return ast.dump(node.left) == expected_obj or ast.dump(node.right) == expected_obj

    def _create_pattern(
        self, node: ast.If, obj_expr: ast.expr, type_name: str
    ) -> IsinstancePattern:
        """Create IsinstancePattern from detected pattern."""
        return IsinstancePattern(
            line_number=node.lineno,
            column=node.col_offset,
            object_name=ast.unparse(obj_expr),
            type_name=type_name,
        )

"""
Purpose: AST-based detector for hasattr LBYL patterns

Scope: Detects 'if hasattr(obj, attr): obj.attr' patterns in Python code

Overview: Provides HasattrDetector class that uses AST traversal to find LBYL anti-patterns
    involving hasattr checking. Identifies patterns where code checks if an object has an
    attribute before accessing it (e.g., 'if hasattr(obj, "attr"): obj.attr'). Returns
    HasattrPattern objects containing the object name, attribute name, and location. Avoids
    false positives for different object/attribute combinations, variable attributes, and
    getattr usage.

Dependencies: ast module, base detector classes from pattern_detectors.base

Exports: HasattrPattern, HasattrDetector

Interfaces: HasattrDetector.find_patterns(tree: ast.AST) -> list[HasattrPattern]

Implementation: AST NodeVisitor pattern with visit_If to detect hasattr check followed by
    attribute access

Suppressions:
    - N802: visit_If follows Python AST visitor naming convention (camelCase required)
    - invalid-name: visit_If follows Python AST visitor naming convention (camelCase required)
"""

import ast
from dataclasses import dataclass

from .base import BaseLBYLDetector, LBYLPattern


@dataclass
class HasattrPattern(LBYLPattern):
    """Pattern data for hasattr LBYL anti-pattern."""

    object_name: str
    attribute_name: str


def _try_extract_hasattr_call(node: ast.expr) -> tuple[ast.expr | None, str | None]:
    """Try to extract hasattr call arguments.

    Returns:
        Tuple of (object_expr, attribute_name) or (None, None) if not a valid hasattr call.
    """
    if not isinstance(node, ast.Call):
        return None, None
    if not isinstance(node.func, ast.Name) or node.func.id != "hasattr":
        return None, None
    return _extract_hasattr_args(node)


def _extract_hasattr_args(call: ast.Call) -> tuple[ast.expr | None, str | None]:
    """Extract object and attribute name from hasattr call args.

    Returns:
        Tuple of (object_expr, attribute_name) or (None, None) if not valid.
    """
    if len(call.args) != 2:
        return None, None

    attr_arg = call.args[1]
    if not isinstance(attr_arg, ast.Constant) or not isinstance(attr_arg.value, str):
        return None, None

    return call.args[0], attr_arg.value


class HasattrDetector(BaseLBYLDetector[HasattrPattern]):
    """Detects 'if hasattr(obj, attr): obj.attr' LBYL patterns."""

    def __init__(self) -> None:
        """Initialize the detector."""
        self._patterns: list[HasattrPattern] = []

    def visit_If(self, node: ast.If) -> None:  # noqa: N802  # pylint: disable=invalid-name
        """Visit if statement to check for hasattr LBYL pattern.

        Args:
            node: AST If node to analyze
        """
        self._check_hasattr_pattern(node)
        self.generic_visit(node)

    def _check_hasattr_pattern(self, node: ast.If) -> None:
        """Check if node is a hasattr LBYL pattern and record it."""
        obj_expr, attr_name = _try_extract_hasattr_call(node.test)
        if obj_expr is None or attr_name is None:
            return

        if self._body_has_attribute_access(node.body, obj_expr, attr_name):
            self._patterns.append(self._create_pattern(node, obj_expr, attr_name))

    def _body_has_attribute_access(
        self, body: list[ast.stmt], obj_expr: ast.expr, attr_name: str
    ) -> bool:
        """Check if body contains obj.attr access matching the hasattr check."""
        expected_obj = ast.dump(obj_expr)
        return any(
            self._is_matching_attribute(node, expected_obj, attr_name)
            for stmt in body
            for node in ast.walk(stmt)
        )

    def _is_matching_attribute(self, node: ast.AST, expected_obj: str, attr_name: str) -> bool:
        """Check if node is an attribute access matching expected object and name."""
        if not isinstance(node, ast.Attribute):
            return False
        return node.attr == attr_name and ast.dump(node.value) == expected_obj

    def _create_pattern(self, node: ast.If, obj_expr: ast.expr, attr_name: str) -> HasattrPattern:
        """Create HasattrPattern from detected pattern."""
        return HasattrPattern(
            line_number=node.lineno,
            column=node.col_offset,
            object_name=ast.unparse(obj_expr),
            attribute_name=attr_name,
        )

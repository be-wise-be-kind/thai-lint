"""
Purpose: AST-based detector for INPUT (query) operations in CQS analysis

Scope: Detects assignment patterns where function call results are captured

Overview: Provides InputDetector class that uses AST traversal to find INPUT operations
    which are query-like assignments that capture function call return values. Detects
    patterns including simple assignments (x = func()), tuple unpacking (x, y = func()),
    async assignments (x = await func()), attribute assignments (self.x = func()),
    subscript assignments (cache[key] = func()), annotated assignments (result: int = func()),
    and walrus operator patterns ((x := func())). Excludes non-call assignments like
    literals, variable copies, and expression results.

Dependencies: ast module for Python AST traversal

Exports: InputDetector

Interfaces: InputDetector.find_inputs(tree: ast.AST) -> list[InputOperation]

Implementation: AST NodeVisitor pattern with visit_Assign, visit_AnnAssign, visit_NamedExpr

Suppressions:
    - N802: visit_Assign, visit_AnnAssign, visit_NamedExpr follow Python AST visitor
        naming convention (camelCase required by ast.NodeVisitor)
    - invalid-name: visit_Assign, visit_AnnAssign, visit_NamedExpr follow Python AST visitor
        naming convention (camelCase required by ast.NodeVisitor)
"""

import ast

from .types import InputOperation


def _is_call_expression(node: ast.expr) -> bool:
    """Check if expression is a Call or Await(Call)."""
    if isinstance(node, ast.Call):
        return True
    if isinstance(node, ast.Await) and isinstance(node.value, ast.Call):
        return True
    return False


def _unwrap_await(node: ast.expr) -> ast.expr:
    """Unwrap Await to get inner expression."""
    if isinstance(node, ast.Await):
        return node.value
    return node


def _extract_target_name(target: ast.expr) -> str:
    """Extract string representation of assignment target."""
    if isinstance(target, ast.Name):
        return target.id
    if isinstance(target, ast.Tuple):
        return ", ".join(_extract_target_name(elt) for elt in target.elts)
    return ast.unparse(target)


class InputDetector(ast.NodeVisitor):
    """Detects INPUT (query) operations that capture function call results."""

    def __init__(self) -> None:
        """Initialize the detector."""
        self._inputs: list[InputOperation] = []

    def find_inputs(self, tree: ast.AST) -> list[InputOperation]:
        """Find INPUT operations in AST.

        Args:
            tree: Python AST to analyze

        Returns:
            List of detected InputOperation objects
        """
        self._inputs = []
        self.visit(tree)
        return list(self._inputs)

    def visit_Assign(self, node: ast.Assign) -> None:  # noqa: N802  # pylint: disable=invalid-name
        """Visit assignment to check for INPUT pattern.

        Detects: x = func(), x, y = func(), self.x = func(), x[key] = func()

        Args:
            node: AST Assign node to analyze
        """
        if _is_call_expression(node.value):
            call_node = _unwrap_await(node.value)
            for target in node.targets:
                self._inputs.append(
                    InputOperation(
                        line=node.lineno,
                        column=node.col_offset,
                        expression=ast.unparse(call_node),
                        target=_extract_target_name(target),
                    )
                )
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:  # noqa: N802  # pylint: disable=invalid-name
        """Visit annotated assignment to check for INPUT pattern.

        Detects: result: int = func()

        Args:
            node: AST AnnAssign node to analyze
        """
        if node.value is not None and node.target is not None:
            if _is_call_expression(node.value):
                call_node = _unwrap_await(node.value)
                self._inputs.append(
                    InputOperation(
                        line=node.lineno,
                        column=node.col_offset,
                        expression=ast.unparse(call_node),
                        target=_extract_target_name(node.target),
                    )
                )
        self.generic_visit(node)

    def visit_NamedExpr(self, node: ast.NamedExpr) -> None:  # noqa: N802  # pylint: disable=invalid-name
        """Visit named expression (walrus operator) to check for INPUT pattern.

        Detects: (x := func())

        Args:
            node: AST NamedExpr node to analyze
        """
        if _is_call_expression(node.value):
            call_node = _unwrap_await(node.value)
            self._inputs.append(
                InputOperation(
                    line=node.lineno,
                    column=node.col_offset,
                    expression=ast.unparse(call_node),
                    target=node.target.id,
                )
            )
        self.generic_visit(node)

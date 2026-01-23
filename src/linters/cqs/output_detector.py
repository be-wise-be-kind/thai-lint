"""
Purpose: AST-based detector for OUTPUT (command) operations in CQS analysis

Scope: Detects statement-level calls where return values are discarded

Overview: Provides OutputDetector class that uses AST traversal to find OUTPUT operations
    which are command-like statement-level function calls that discard return values.
    Detects patterns including statement calls (func()), async statements (await func()),
    method calls (obj.method()), and chained calls (obj.method().method2()). Only ast.Expr
    nodes containing Call or Await(Call) are detected as OUTPUT. All other constructs
    (return, if, while, for, with, assert, raise, yield, assignments, comprehensions)
    are naturally excluded because they use different AST node types.

Dependencies: ast module for Python AST traversal

Exports: OutputDetector

Interfaces: OutputDetector.find_outputs(tree: ast.AST) -> list[OutputOperation]

Implementation: AST NodeVisitor pattern with visit_Expr to detect statement-level calls

Suppressions:
    - N802: visit_Expr follows Python AST visitor naming convention
        (camelCase required by ast.NodeVisitor)
    - invalid-name: visit_Expr follows Python AST visitor naming convention
        (camelCase required by ast.NodeVisitor)
"""

import ast

from .types import OutputOperation


def _extract_call_expression(node: ast.expr) -> ast.Call | None:
    """Extract Call from expression, unwrapping Await if present."""
    if isinstance(node, ast.Call):
        return node
    if isinstance(node, ast.Await) and isinstance(node.value, ast.Call):
        return node.value
    return None


class OutputDetector(ast.NodeVisitor):
    """Detects OUTPUT (command) operations that discard function call results."""

    def __init__(self) -> None:
        """Initialize the detector."""
        self._outputs: list[OutputOperation] = []

    def find_outputs(self, tree: ast.AST) -> list[OutputOperation]:
        """Find OUTPUT operations in AST.

        Args:
            tree: Python AST to analyze

        Returns:
            List of detected OutputOperation objects
        """
        self._outputs = []
        self.visit(tree)
        return list(self._outputs)

    def visit_Expr(self, node: ast.Expr) -> None:  # noqa: N802  # pylint: disable=invalid-name
        """Visit expression statement to check for OUTPUT pattern.

        Only statement-level expressions (ast.Expr) are OUTPUT. This naturally
        excludes return statements, conditionals, assignments, comprehensions,
        and other constructs that use the call result.

        Detects: func(), await func(), obj.method(), obj.method().method2()

        Args:
            node: AST Expr node to analyze
        """
        call_node = _extract_call_expression(node.value)
        if call_node is not None:
            self._outputs.append(
                OutputOperation(
                    line=node.lineno,
                    column=node.col_offset,
                    expression=ast.unparse(call_node),
                )
            )
        self.generic_visit(node)

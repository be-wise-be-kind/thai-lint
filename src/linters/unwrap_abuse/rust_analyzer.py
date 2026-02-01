"""
Purpose: Analyzer for detecting unwrap/expect abuse in Rust code using tree-sitter AST

Scope: Pattern detection for .unwrap() and .expect() method calls in Rust source files

Overview: Provides RustUnwrapAnalyzer that extends RustBaseAnalyzer to detect .unwrap() and
    .expect() method calls in Rust code. Uses tree-sitter AST to find call_expression nodes
    containing field_expression with field_identifier matching "unwrap" or "expect". Determines
    whether each call is inside test code using the base analyzer's is_inside_test() method.
    Returns structured UnwrapCall dataclass instances with location, method name, test context,
    and surrounding code for violation reporting.

Dependencies: src.analyzers.rust_base for tree-sitter parsing and traversal

Exports: RustUnwrapAnalyzer, UnwrapCall

Interfaces: find_unwrap_calls(code: str) -> list[UnwrapCall]

Implementation: Recursive AST traversal with field_expression pattern matching for method calls
"""

from dataclasses import dataclass

from src.analyzers.rust_base import TREE_SITTER_RUST_AVAILABLE, RustBaseAnalyzer

if TREE_SITTER_RUST_AVAILABLE:
    from tree_sitter import Node


@dataclass
class UnwrapCall:
    """Represents a detected unwrap/expect call."""

    line: int
    column: int
    method: str  # "unwrap" or "expect"
    is_in_test: bool
    context: str  # Surrounding code snippet


class RustUnwrapAnalyzer(RustBaseAnalyzer):
    """Analyzer for detecting unwrap/expect calls in Rust code."""

    def find_unwrap_calls(self, code: str) -> list[UnwrapCall]:
        """Find all unwrap() and expect() calls in code.

        Args:
            code: Rust source code to analyze

        Returns:
            List of detected unwrap/expect calls with location and context
        """
        if not self.tree_sitter_available:
            return []

        root = self.parse_rust(code)
        if root is None:
            return []

        calls: list[UnwrapCall] = []
        self._find_unwrap_recursive(root, code, calls)
        return calls

    def _find_unwrap_recursive(self, node: "Node", code: str, calls: list[UnwrapCall]) -> None:
        """Recursively find unwrap/expect method calls in AST.

        Args:
            node: Current tree-sitter node to inspect
            code: Original source code for context extraction
            calls: Accumulator list for detected calls
        """
        if node.type == "call_expression":
            method_name = self._get_method_name(node)
            if method_name in ("unwrap", "expect"):
                calls.append(
                    UnwrapCall(
                        line=node.start_point[0] + 1,
                        column=node.start_point[1],
                        method=method_name,
                        is_in_test=self.is_inside_test(node),
                        context=_get_line_context(code, node.start_point[0]),
                    )
                )

        for child in node.children:
            self._find_unwrap_recursive(child, code, calls)

    def _get_method_name(self, call_node: "Node") -> str:
        """Extract method name from a call expression.

        In Rust tree-sitter, method calls have this structure:
            call_expression -> field_expression -> field_identifier

        Args:
            call_node: A call_expression node

        Returns:
            Method name string, or empty string if not a method call
        """
        for child in call_node.children:
            if child.type == "field_expression":
                return self._extract_field_identifier(child)
        return ""

    def _extract_field_identifier(self, field_expr: "Node") -> str:
        """Extract the field identifier from a field expression.

        Args:
            field_expr: A field_expression node

        Returns:
            The field identifier text (e.g., "unwrap", "expect")
        """
        for subchild in field_expr.children:
            if subchild.type == "field_identifier":
                return self.extract_node_text(subchild)
        return ""


def _get_line_context(code: str, line_index: int) -> str:
    """Get the code line at the given index for context.

    Args:
        code: Full source code
        line_index: Zero-indexed line number

    Returns:
        Stripped line content, or empty string if index out of range
    """
    lines = code.split("\n")
    if 0 <= line_index < len(lines):
        return lines[line_index].strip()
    return ""

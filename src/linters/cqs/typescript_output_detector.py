"""
Purpose: Tree-sitter based detector for OUTPUT (command) operations in TypeScript CQS analysis

Scope: Detects statement-level calls where return values are discarded in TypeScript code

Overview: Provides TypeScriptOutputDetector class that uses tree-sitter AST traversal to find
    OUTPUT operations in TypeScript code. OUTPUT operations are command-like statement-level
    function calls that discard return values. Detects patterns including statement calls
    (func();), async statement calls (await func();), method calls (obj.method();), and
    chained method calls (obj.method().method2();). Only expression_statement nodes containing
    call_expression or await_expression are detected as OUTPUT. Naturally excludes return
    statements, conditionals, assignments, and other constructs that use call results.

Dependencies: tree-sitter via TypeScriptBaseAnalyzer

Exports: TypeScriptOutputDetector

Interfaces: TypeScriptOutputDetector.find_outputs(root_node) -> list[OutputOperation]

Implementation: Tree-sitter AST traversal targeting expression_statement nodes
"""

from src.analyzers.typescript_base import (
    TREE_SITTER_AVAILABLE,
    Node,
    TypeScriptBaseAnalyzer,
)

from .types import OutputOperation


class TypeScriptOutputDetector(TypeScriptBaseAnalyzer):
    """Detects OUTPUT (command) operations that discard function call results in TypeScript."""

    def find_outputs(self, root_node: Node) -> list[OutputOperation]:
        """Find OUTPUT operations in TypeScript AST.

        Args:
            root_node: Tree-sitter AST root node to analyze

        Returns:
            List of detected OutputOperation objects
        """
        if not TREE_SITTER_AVAILABLE or root_node is None:
            return []

        outputs: list[OutputOperation] = []
        self._find_outputs_recursive(root_node, outputs)
        return outputs

    def _find_outputs_recursive(self, node: Node, outputs: list[OutputOperation]) -> None:
        """Recursively find OUTPUT operations in AST.

        Only expression_statement containing call_expression or await_expression
        with call_expression are OUTPUT operations.

        Args:
            node: Current tree-sitter node
            outputs: List to accumulate OutputOperation objects
        """
        if node.type == "expression_statement":
            self._check_expression_statement(node, outputs)

        # Recurse into children
        for child in node.children:
            self._find_outputs_recursive(child, outputs)

    def _check_expression_statement(self, node: Node, outputs: list[OutputOperation]) -> None:
        """Check expression statement for OUTPUT pattern.

        Handles: func();, await func();, obj.method();

        Args:
            node: expression_statement node
            outputs: List to append outputs to
        """
        call_node = self._find_call_in_expression(node)
        if call_node is None:
            return

        expression = self.extract_node_text(call_node)
        line = node.start_point[0] + 1
        column = node.start_point[1]

        outputs.append(OutputOperation(line=line, column=column, expression=expression))

    def _find_call_in_expression(self, node: Node) -> Node | None:
        """Find call expression in expression statement.

        Handles direct calls and await expressions containing calls.

        Args:
            node: expression_statement node

        Returns:
            call_expression node or None
        """
        for child in node.children:
            if child.type == "call_expression":
                return child
            if child.type == "await_expression":
                return self._find_call_in_await(child)
        return None

    def _find_call_in_await(self, node: Node) -> Node | None:
        """Find call expression inside await expression.

        Args:
            node: await_expression node

        Returns:
            call_expression node or None
        """
        for child in node.children:
            if child.type == "call_expression":
                return child
        return None

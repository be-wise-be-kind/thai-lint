"""
Purpose: Tree-sitter based detector for INPUT (query) operations in TypeScript CQS analysis

Scope: Detects assignment patterns where function call results are captured in TypeScript code

Overview: Provides TypeScriptInputDetector class that uses tree-sitter AST traversal to find
    INPUT operations in TypeScript code. INPUT operations are query-like assignments that
    capture function call return values. Detects patterns including variable declarations
    (const x = func(), let x = func()), destructuring (const { a, b } = func(),
    const [a, b] = func()), await assignments (const x = await func()), and class field
    assignments (this.x = func()). Uses tree-sitter node types lexical_declaration,
    variable_declarator, assignment_expression, and call_expression for detection.

Dependencies: tree-sitter via TypeScriptBaseAnalyzer

Exports: TypeScriptInputDetector

Interfaces: TypeScriptInputDetector.find_inputs(root_node) -> list[InputOperation]

Implementation: Tree-sitter AST traversal with recursive node collection
"""

from collections.abc import Callable
from typing import Any

from src.analyzers.typescript_base import (
    TREE_SITTER_AVAILABLE,
    Node,
    TypeScriptBaseAnalyzer,
)

from .types import InputOperation

# Module-level helper functions for AST navigation


def _find_child_by_type(node: Node, types: set[str]) -> Node | None:
    """Find first child matching any of the given types."""
    return next((child for child in node.children if child.type in types), None)


def _find_children_after_token(node: Node, token: str) -> list[Node]:
    """Get all children after a specific token."""
    children = list(node.children)
    for i, child in enumerate(children):
        if child.type == token:
            return children[i + 1 :]
    return []


def _find_after_token(node: Node, token: str, exclude_types: set[str] | None = None) -> Node | None:
    """Find first child after a specific token, excluding certain types."""
    exclude = exclude_types or set()
    remaining = _find_children_after_token(node, token)
    return next((c for c in remaining if c.type not in exclude), None)


def _find_declarator_name(node: Node) -> Node | None:
    """Find name/pattern node in variable declarator."""
    return _find_child_by_type(node, {"identifier", "object_pattern", "array_pattern"})


def _find_declarator_value(node: Node) -> Node | None:
    """Find value node in variable declarator (after =)."""
    return _find_after_token(node, "=", {":", "type_annotation"})


def _find_assignment_left(node: Node) -> Node | None:
    """Find left side of assignment expression."""
    return _find_child_by_type(node, {"identifier", "member_expression", "subscript_expression"})


def _find_assignment_right(node: Node) -> Node | None:
    """Find right side of assignment expression (after =)."""
    return _find_after_token(node, "=")


def _extract_call_from_value(node: Node) -> Node | None:
    """Extract call expression from value, handling await wrapper."""
    if node.type == "call_expression":
        return node
    if node.type == "await_expression":
        return next((c for c in node.children if c.type == "call_expression"), None)
    return None


def _find_pattern_value(pair_node: Node) -> Any:
    """Find value identifier in pair pattern (e.g., a: b -> returns 'b')."""
    children_after_colon = _find_children_after_token(pair_node, ":")
    return next((c for c in children_after_colon if c.type == "identifier"), None)


def _get_pattern_child_name(child: Node, get_text: Callable[[Node], str]) -> str | None:
    """Extract name from an object pattern child node."""
    if child.type == "shorthand_property_identifier_pattern":
        return get_text(child)
    if child.type == "pair_pattern":
        value = _find_pattern_value(child)
        return get_text(value) if value else None
    return None


def _extract_object_pattern_names(node: Node, get_text: Callable[[Node], str]) -> str:
    """Extract names from object destructuring pattern."""
    names = [
        name
        for child in node.children
        if (name := _get_pattern_child_name(child, get_text)) is not None
    ]
    return ", ".join(names) if names else get_text(node)


def _extract_array_pattern_names(node: Node, get_text: Callable[[Node], str]) -> str:
    """Extract names from array destructuring pattern."""
    names = [get_text(child) for child in node.children if child.type == "identifier"]
    return ", ".join(names) if names else get_text(node)


def _extract_target_name(name_node: Node, get_text: Callable[[Node], str]) -> str:
    """Extract string representation of assignment target."""
    if name_node.type == "identifier":
        return get_text(name_node)
    if name_node.type == "object_pattern":
        return _extract_object_pattern_names(name_node, get_text)
    if name_node.type == "array_pattern":
        return _extract_array_pattern_names(name_node, get_text)
    return get_text(name_node)


class TypeScriptInputDetector(TypeScriptBaseAnalyzer):
    """Detects INPUT (query) operations that capture function call results in TypeScript."""

    def find_inputs(self, root_node: Node) -> list[InputOperation]:
        """Find INPUT operations in TypeScript AST."""
        if not TREE_SITTER_AVAILABLE or root_node is None:
            return []
        inputs: list[InputOperation] = []
        self._find_inputs_recursive(root_node, inputs)
        return inputs

    def _find_inputs_recursive(self, node: Node, inputs: list[InputOperation]) -> None:
        """Recursively find INPUT operations in AST."""
        if node.type == "lexical_declaration":
            self._check_lexical_declaration(node, inputs)
        elif node.type == "assignment_expression":
            self._check_assignment_expression(node, inputs)

        for child in node.children:
            self._find_inputs_recursive(child, inputs)

    def _check_lexical_declaration(self, node: Node, inputs: list[InputOperation]) -> None:
        """Check lexical declaration for INPUT patterns."""
        for child in node.children:
            if child.type == "variable_declarator":
                self._check_variable_declarator(child, inputs)

    def _check_variable_declarator(self, node: Node, inputs: list[InputOperation]) -> None:
        """Check variable declarator for call expression assignment."""
        name_node = _find_declarator_name(node)
        value_node = _find_declarator_value(node)

        if name_node is None or value_node is None:
            return

        call_node = _extract_call_from_value(value_node)
        if call_node is None:
            return

        inputs.append(self._create_input_operation(node, name_node, call_node))

    def _check_assignment_expression(self, node: Node, inputs: list[InputOperation]) -> None:
        """Check assignment expression for INPUT pattern (this.x = func())."""
        left_node = _find_assignment_left(node)
        right_node = _find_assignment_right(node)

        if left_node is None or right_node is None:
            return

        call_node = _extract_call_from_value(right_node)
        if call_node is None:
            return

        target = self.extract_node_text(left_node)
        expression = self.extract_node_text(call_node)
        inputs.append(
            InputOperation(
                line=node.start_point[0] + 1,
                column=node.start_point[1],
                expression=expression,
                target=target,
            )
        )

    def _create_input_operation(
        self, node: Node, name_node: Node, call_node: Node
    ) -> InputOperation:
        """Create an InputOperation from parsed nodes."""
        return InputOperation(
            line=node.start_point[0] + 1,
            column=node.start_point[1],
            expression=self.extract_node_text(call_node),
            target=_extract_target_name(name_node, self.extract_node_text),
        )

"""
Purpose: Analyzer for detecting clone abuse patterns in Rust code using tree-sitter AST

Scope: Pattern detection for .clone() method calls including loop, chain, and unnecessary patterns

Overview: Provides RustCloneAnalyzer that extends RustBaseAnalyzer to detect .clone() abuse
    patterns in Rust code. Detects three patterns: clone-in-loop (clone calls inside for,
    while, or loop bodies), clone-chain (chained .clone().clone() calls), and unnecessary-clone
    (clone in let binding where the source identifier is not used again in the enclosing block).
    Uses tree-sitter AST to find call_expression nodes with field_identifier matching "clone"
    and classifies each call by walking the AST structure. Returns structured CloneCall dataclass
    instances with location, pattern type, test context, and surrounding code for violation reporting.

Dependencies: src.analyzers.rust_base for tree-sitter parsing and traversal

Exports: RustCloneAnalyzer, CloneCall

Interfaces: find_clone_calls(code: str) -> list[CloneCall]

Implementation: Recursive AST traversal with pattern classification using parent-chain walking
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from src.analyzers.rust_base import RustBaseAnalyzer
from src.core.linter_utils import get_line_context

if TYPE_CHECKING:
    from tree_sitter import Node

_LOOP_NODE_TYPES = frozenset({"for_expression", "while_expression", "loop_expression"})


@dataclass
class CloneCall:
    """Represents a detected clone call with its abuse pattern."""

    line: int
    column: int
    pattern: str  # "clone-in-loop", "clone-chain", "unnecessary-clone"
    is_in_test: bool
    context: str  # Surrounding code snippet


class RustCloneAnalyzer(RustBaseAnalyzer):
    """Analyzer for detecting clone abuse patterns in Rust code."""

    def find_clone_calls(self, code: str) -> list[CloneCall]:
        """Find all abusive .clone() calls in code.

        Args:
            code: Rust source code to analyze

        Returns:
            List of detected clone calls with pattern classification
        """
        if not self.tree_sitter_available:
            return []

        root = self.parse_rust(code)
        if root is None:
            return []

        calls: list[CloneCall] = []
        self._find_clone_recursive(root, code, calls)
        return calls

    def _find_clone_recursive(self, node: Node, code: str, calls: list[CloneCall]) -> None:
        """Recursively find abusive clone calls in AST.

        Args:
            node: Current tree-sitter node to inspect
            code: Original source code for context extraction
            calls: Accumulator list for detected calls
        """
        if node.type == "call_expression":
            method_name = self._get_method_name(node)
            if method_name == "clone":
                pattern = self._classify_clone(node, code)
                if pattern is not None:
                    calls.append(
                        CloneCall(
                            line=node.start_point[0] + 1,
                            column=node.start_point[1],
                            pattern=pattern,
                            is_in_test=self.is_inside_test(node),
                            context=get_line_context(code, node.start_point[0]),
                        )
                    )

        for child in node.children:
            self._find_clone_recursive(child, code, calls)

    def _get_method_name(self, call_node: Node) -> str:
        """Extract method name from a call expression.

        Args:
            call_node: A call_expression node

        Returns:
            Method name string, or empty string if not a method call
        """
        for child in call_node.children:
            if child.type == "field_expression":
                return self._extract_field_identifier(child)
        return ""

    def _extract_field_identifier(self, field_expr: Node) -> str:
        """Extract the field identifier from a field expression.

        Args:
            field_expr: A field_expression node

        Returns:
            The field identifier text (e.g., "clone")
        """
        for subchild in field_expr.children:
            if subchild.type == "field_identifier":
                return self.extract_node_text(subchild)
        return ""

    def _classify_clone(self, node: Node, code: str) -> str | None:
        """Classify a clone call into an abuse pattern.

        Checks patterns in priority order: chain, loop, unnecessary.
        Returns None if the clone does not match any abuse pattern.

        Args:
            node: The call_expression node for the .clone() call
            code: Original source code

        Returns:
            Pattern string or None if not abusive
        """
        _ = code
        if self._is_chained_clone(node):
            return "clone-chain"
        if self._is_inside_loop(node):
            return "clone-in-loop"
        if self._is_unnecessary_clone(node):
            return "unnecessary-clone"
        return None

    def _is_inside_loop(self, node: Node) -> bool:
        """Check if node is inside a loop body.

        Walks the parent chain looking for loop node types.

        Args:
            node: Node to check

        Returns:
            True if inside a for, while, or loop expression
        """
        current: Node | None = node.parent
        while current is not None:
            if current.type in _LOOP_NODE_TYPES:
                return True
            current = current.parent
        return False

    def _is_chained_clone(self, node: Node) -> bool:
        """Check if this clone's receiver is itself a .clone() call.

        Detects patterns like data.clone().clone() where the outer clone's
        receiver (via field_expression) is a call_expression with method "clone".

        Args:
            node: The call_expression node for this .clone() call

        Returns:
            True if this clone is chained on another clone
        """
        field_expr = _get_field_expression(node)
        if field_expr is None:
            return False
        receiver = _get_receiver_node(field_expr)
        if receiver is None or receiver.type != "call_expression":
            return False
        return self._get_method_name(receiver) == "clone"

    def _is_unnecessary_clone(self, node: Node) -> bool:
        """Check if clone is unnecessary (source not used after cloning).

        Only flags when ALL conditions are met:
        - The clone is in a let declaration: let x = y.clone();
        - The receiver y is a simple identifier (not self.field, not foo.bar())
        - y does not appear in any subsequent statement in the same block

        Args:
            node: The call_expression node for this .clone() call

        Returns:
            True if the clone appears unnecessary
        """
        let_node = _find_parent_let_declaration(node)
        if let_node is None:
            return False

        identifier = self._get_clone_receiver_identifier(node)
        if identifier is None:
            return False

        block_node = _find_parent_block(let_node)
        if block_node is None:
            return False

        return not _identifier_used_after(identifier, let_node, block_node)

    def _get_clone_receiver_identifier(self, node: Node) -> str | None:
        """Extract the simple identifier being cloned.

        Returns None for complex expressions like self.field or foo.bar().

        Args:
            node: The call_expression node for this .clone() call

        Returns:
            Simple identifier string, or None for complex receivers
        """
        field_expr = _get_field_expression(node)
        if field_expr is None:
            return None
        receiver = _get_receiver_node(field_expr)
        if receiver is None:
            return None
        if receiver.type != "identifier":
            return None
        return self.extract_node_text(receiver)


def _get_field_expression(call_node: Node) -> Node | None:
    """Get the field_expression child of a call_expression.

    Args:
        call_node: A call_expression node

    Returns:
        The field_expression child, or None
    """
    for child in call_node.children:
        if child.type == "field_expression":
            return child
    return None


def _get_receiver_node(field_expr: Node) -> Node | None:
    """Get the receiver (first child) of a field_expression.

    In Rust tree-sitter, field_expression children are:
    [receiver, ".", field_identifier]

    Args:
        field_expr: A field_expression node

    Returns:
        The receiver node, or None
    """
    children = field_expr.children
    if children:
        return children[0]
    return None


def _find_parent_let_declaration(node: Node) -> Node | None:
    """Find the enclosing let_declaration for a node.

    Args:
        node: Starting node to search from

    Returns:
        The let_declaration node, or None if not inside one
    """
    current: Node | None = node.parent
    while current is not None:
        if current.type == "let_declaration":
            return current
        if current.type in ("block", "function_item"):
            return None
        current = current.parent
    return None


def _find_parent_block(node: Node) -> Node | None:
    """Find the enclosing block for a node.

    Args:
        node: Starting node to search from

    Returns:
        The block node, or None
    """
    current: Node | None = node.parent
    while current is not None:
        if current.type == "block":
            return current
        current = current.parent
    return None


def _identifier_used_after(identifier: str, let_node: Node, block_node: Node) -> bool:
    """Check if identifier appears in statements after let_node in the block.

    Scans subsequent siblings of let_node within block_node for any reference
    to the given identifier.

    Args:
        identifier: The variable name to search for
        let_node: The let_declaration node
        block_node: The enclosing block node

    Returns:
        True if identifier is referenced after the let_node
    """
    found_let = False
    for child in block_node.children:
        if child.id == let_node.id:
            found_let = True
            continue
        if found_let and _node_contains_identifier(child, identifier):
            return True
    return False


def _node_contains_identifier(node: Node, identifier: str) -> bool:
    """Recursively check if a node or its descendants contain an identifier reference.

    Args:
        node: Node to search in
        identifier: Identifier name to look for

    Returns:
        True if the identifier is found
    """
    if _is_matching_identifier(node, identifier):
        return True
    return any(_node_contains_identifier(child, identifier) for child in node.children)


def _is_matching_identifier(node: Node, identifier: str) -> bool:
    """Check if a node is an identifier matching the given name.

    Args:
        node: Node to check
        identifier: Expected identifier name

    Returns:
        True if node is an identifier with the given name
    """
    if node.type != "identifier":
        return False
    text = node.text
    return text is not None and text.decode() == identifier

"""
Purpose: Extract chain parts from Python AST nodes

Scope: Walking AST Attribute/Call/Subscript nodes to produce list[str] chain representations

Overview: Provides the chain_to_parts() function that walks an AST node and extracts a list
    of string parts representing the chain of attribute accesses and method calls. Method calls
    are marked with "()", subscript accesses with "[...]". Also provides helper functions for
    cleaning and classifying chain parts.

Dependencies: ast

Exports: chain_to_parts, clean_part, is_subscript_part

Interfaces: chain_to_parts(node: ast.AST) -> list[str]

Implementation: Iterative walk from outer to inner AST node, reversing to get left-to-right order
"""

import ast

SUBSCRIPT_MARKER = "[\u2026]"


def _call_suffix(pending: bool) -> str:
    """Return '()' if a call is pending, else empty string."""
    return "()" if pending else ""


def chain_to_parts(node: ast.AST) -> list[str]:
    """Walk an AST node and extract the chain of attribute/method names.

    Returns list of parts like ["obj", "method()", "attr", "[...]"].

    Args:
        node: AST node (Attribute, Call, Subscript, or Name)

    Returns:
        List of chain parts in left-to-right order
    """
    parts: list[str] = []
    current: ast.AST | None = node
    pending_call = False

    while current is not None:
        current, pending_call = _process_node(current, parts, pending_call)

    parts.reverse()
    return parts


def _process_node(
    current: ast.AST, parts: list[str], pending_call: bool
) -> tuple[ast.AST | None, bool]:
    """Process a single AST node during chain extraction.

    Returns (next_node, pending_call) or (None, _) to stop iteration.
    """
    if isinstance(current, ast.Attribute):
        parts.append(current.attr + _call_suffix(pending_call))
        return current.value, False
    if isinstance(current, ast.Call):
        return current.func, True
    if isinstance(current, ast.Subscript):
        parts.append(SUBSCRIPT_MARKER)
        return current.value, False
    # Terminal nodes: Name or unknown
    name = current.id if isinstance(current, ast.Name) else "?"
    parts.append(name + _call_suffix(pending_call))
    return None, False


def clean_part(part: str) -> str:
    """Strip () and [...] markers from a chain part.

    Args:
        part: Chain part string, possibly with markers

    Returns:
        Cleaned part name without markers
    """
    return part.replace(SUBSCRIPT_MARKER, "").rstrip("()")


def is_subscript_part(part: str) -> bool:
    """Check if a chain part represents a subscript access.

    Args:
        part: Chain part string

    Returns:
        True if the part is a subscript marker
    """
    return SUBSCRIPT_MARKER in part

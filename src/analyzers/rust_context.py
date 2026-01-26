"""
Purpose: Rust-specific AST context detection utilities

Scope: Helper functions for detecting test contexts and async functions in Rust code

Overview: Provides standalone helper functions for analyzing Rust AST context information.
    Includes functions for detecting if code is inside a test function or module by checking
    for #[test] or #[cfg(test)] attributes on preceding siblings, and for detecting async
    functions by checking for function_modifiers. These utilities are designed to be used
    in composition with RustBaseAnalyzer for Rust-specific lint rules that need to understand
    code context.

Dependencies: tree-sitter (for Node type when available)

Exports: is_inside_test, is_async_function, has_test_attribute, has_cfg_test_attribute

Interfaces: All functions take tree-sitter Node objects and return bool

Implementation: Sibling-based attribute lookup for Rust AST structure, iterative parent
    traversal for context detection

Suppressions:
    - misc,assignment: Node type alias when tree-sitter optional dependency unavailable
"""

from typing import Any

try:
    from tree_sitter import Node

    TREE_SITTER_AVAILABLE = True
except ImportError:
    TREE_SITTER_AVAILABLE = False
    Node = Any  # type: ignore[misc,assignment]


def _get_node_text(node: Node) -> str:
    """Get decoded text from a node.

    Args:
        node: Tree-sitter node

    Returns:
        Decoded text content
    """
    return node.text.decode() if node.text else ""


def has_test_attribute(function_node: Node) -> bool:
    """Check if a function has #[test] attribute as preceding sibling.

    Args:
        function_node: Function item node

    Returns:
        True if function has #[test] attribute
    """
    prev_sibling = function_node.prev_sibling
    while prev_sibling is not None and prev_sibling.type == "attribute_item":
        if "test" in _get_node_text(prev_sibling):
            return True
        prev_sibling = prev_sibling.prev_sibling
    return False


def has_cfg_test_attribute(mod_node: Node) -> bool:
    """Check if a module has #[cfg(test)] attribute as preceding sibling.

    Args:
        mod_node: Module item node

    Returns:
        True if module has #[cfg(test)] attribute
    """
    prev_sibling = mod_node.prev_sibling
    while prev_sibling is not None and prev_sibling.type == "attribute_item":
        if "cfg(test)" in _get_node_text(prev_sibling):
            return True
        prev_sibling = prev_sibling.prev_sibling
    return False


def is_inside_test(node: Node) -> bool:
    """Check if node is inside a test function or module.

    Walks up the tree looking for #[test] or #[cfg(test)] attributes.

    Args:
        node: Tree-sitter node to check

    Returns:
        True if the node is inside a test function or test module
    """
    current: Node | None = node
    while current is not None:
        if _is_test_context(current):
            return True
        current = current.parent
    return False


def _is_test_context(node: Node) -> bool:
    """Check if a node represents a test context.

    Args:
        node: Node to check

    Returns:
        True if node is a test function or test module
    """
    if node.type == "function_item":
        return has_test_attribute(node)
    if node.type == "mod_item":
        return has_cfg_test_attribute(node)
    return False


def is_async_function(node: Node) -> bool:
    """Check if a function_item is async.

    Args:
        node: Function item node to check

    Returns:
        True if the function is declared as async
    """
    return any(
        child.type == "function_modifiers" and _has_async_modifier(child) for child in node.children
    )


def _has_async_modifier(modifiers_node: Node) -> bool:
    """Check if function_modifiers node contains async keyword.

    Args:
        modifiers_node: The function_modifiers node

    Returns:
        True if async keyword is present
    """
    return any(modifier.type == "async" for modifier in modifiers_node.children)

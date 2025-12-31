"""
Purpose: Common Python AST utilities for linter analyzers

Scope: Shared AST traversal utilities for Python code analysis

Overview: Provides common AST utility functions used across multiple Python linters.
    Centralizes shared patterns like parent map building to eliminate code duplication.
    The build_parent_map function creates a dictionary mapping AST nodes to their parents,
    enabling upward tree traversal for context detection.

Dependencies: ast module for AST node types

Exports: build_parent_map

Interfaces: build_parent_map(tree: ast.AST) -> dict[ast.AST, ast.AST]

Implementation: Recursive AST traversal with parent tracking
"""

import ast


def build_parent_map(tree: ast.AST) -> dict[ast.AST, ast.AST]:
    """Build a map of AST nodes to their parent nodes.

    Enables upward tree traversal for context detection (e.g., finding if a node
    is inside a particular block type).

    Args:
        tree: Root AST node to build map from

    Returns:
        Dictionary mapping each node to its parent node
    """
    parent_map: dict[ast.AST, ast.AST] = {}
    _build_parent_map_recursive(tree, None, parent_map)
    return parent_map


def _build_parent_map_recursive(
    node: ast.AST, parent: ast.AST | None, parent_map: dict[ast.AST, ast.AST]
) -> None:
    """Recursively build parent map.

    Args:
        node: Current AST node
        parent: Parent of current node
        parent_map: Dictionary to populate
    """
    if parent is not None:
        parent_map[node] = parent

    for child in ast.iter_child_nodes(node):
        _build_parent_map_recursive(child, node, parent_map)

"""
Purpose: Shared AST utility functions for collection pipeline analyzers

Scope: Common patterns for analyzing function bodies and return statements

Overview: Provides reusable AST analysis helpers to reduce duplication across
    any_all_analyzer, filter_map_analyzer, and other pattern detection modules.
    Centralizes common patterns like finding return statements after for loops.

Dependencies: ast module

Exports: get_next_return_stmt

Interfaces: get_next_return_stmt(func_body, index) -> ast.Return | None

Implementation: Pure functions using Python ast module for AST node inspection
"""

import ast


def get_next_return_stmt(func_body: list[ast.stmt], current_index: int) -> ast.Return | None:
    """Get the next return statement after a given index, if it exists.

    Args:
        func_body: List of statements in function body
        current_index: Index of the current statement (e.g., for loop)

    Returns:
        The Return statement if the next statement is a return, None otherwise
    """
    next_index = current_index + 1
    if next_index >= len(func_body):
        return None

    stmt = func_body[next_index]
    if not isinstance(stmt, ast.Return):
        return None

    return stmt

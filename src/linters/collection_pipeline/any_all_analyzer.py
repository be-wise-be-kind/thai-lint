"""
Purpose: Analyze any()/all() anti-patterns in for loops

Scope: Extract and validate loops that return True/False and could use any()/all()

Overview: Provides helper functions for analyzing loops that iterate and return boolean
    values based on conditions. Detects patterns like 'for x in iter: if cond: return True;
    return False' which can be refactored to 'return any(cond for x in iter)'. Also handles
    the inverse all() pattern. Requires function context to analyze return statements.

Dependencies: ast module for Python AST processing

Exports: extract_any_pattern, extract_all_pattern, AnyAllMatch dataclass

Interfaces: Functions for analyzing any/all patterns in AST function bodies

Implementation: AST-based pattern matching for any/all pattern identification
"""

import ast
from dataclasses import dataclass
from typing import cast

from . import ast_utils


@dataclass
class AnyAllMatch:
    """Information about a detected any()/all() pattern."""

    for_node: ast.For
    """The for loop AST node."""

    condition: ast.expr
    """The condition expression inside the if statement."""

    is_any: bool
    """True for any() pattern, False for all() pattern."""


def extract_any_pattern(func_body: list[ast.stmt], for_node: ast.For) -> AnyAllMatch | None:
    """Extract any() pattern from a for loop in a function body.

    Pattern: for x in iter: if cond: return True; return False

    Args:
        func_body: List of statements in the function body
        for_node: The for loop AST node to analyze

    Returns:
        AnyAllMatch if pattern detected, None otherwise
    """
    # Check for/else - different semantics, skip
    if for_node.orelse:
        return None

    # Check loop body has exactly one if statement with return True
    if_return_true = _extract_if_return_true(for_node.body)
    if if_return_true is None:
        return None

    # Find position of for loop in function body
    for_index = _get_stmt_index(func_body, for_node)
    if for_index is None:
        return None

    # Check next statement is return False
    if not _is_next_stmt_return_false(func_body, for_index):
        return None

    return AnyAllMatch(
        for_node=for_node,
        condition=if_return_true.test,
        is_any=True,
    )


def extract_all_pattern(func_body: list[ast.stmt], for_node: ast.For) -> AnyAllMatch | None:
    """Extract all() pattern from a for loop in a function body.

    Pattern: for x in iter: if not cond: return False; return True

    Args:
        func_body: List of statements in the function body
        for_node: The for loop AST node to analyze

    Returns:
        AnyAllMatch if pattern detected, None otherwise
    """
    # Check for/else - different semantics, skip
    if for_node.orelse:
        return None

    # Check loop body has exactly one if statement with return False
    if_return_false = _extract_if_return_false(for_node.body)
    if if_return_false is None:
        return None

    # Find position of for loop in function body
    for_index = _get_stmt_index(func_body, for_node)
    if for_index is None:
        return None

    # Check next statement is return True
    if not _is_next_stmt_return_true(func_body, for_index):
        return None

    # Invert the condition for all() suggestion
    condition = _invert_condition(if_return_false.test)

    return AnyAllMatch(
        for_node=for_node,
        condition=condition,
        is_any=False,
    )


def _is_simple_if_return(stmt: ast.stmt) -> ast.Return | None:
    """Check if statement is simple if with single return and no else.

    Args:
        stmt: Statement to check

    Returns:
        The return statement if pattern matches, None otherwise
    """
    if not isinstance(stmt, ast.If):
        return None
    if stmt.orelse:
        return None
    if len(stmt.body) != 1:
        return None
    if not isinstance(stmt.body[0], ast.Return):
        return None
    return stmt.body[0]


def _extract_if_return_true(body: list[ast.stmt]) -> ast.If | None:
    """Extract if statement that only contains return True.

    Args:
        body: List of statements in for loop body

    Returns:
        The if statement if pattern matches, None otherwise
    """
    if len(body) != 1:
        return None

    stmt = body[0]
    return_stmt = _is_simple_if_return(stmt)
    if return_stmt is None:
        return None

    if not _is_literal_true(return_stmt.value):
        return None

    return cast(ast.If, stmt)


def _extract_if_return_false(body: list[ast.stmt]) -> ast.If | None:
    """Extract if statement that only contains return False.

    Args:
        body: List of statements in for loop body

    Returns:
        The if statement if pattern matches, None otherwise
    """
    if len(body) != 1:
        return None

    stmt = body[0]
    return_stmt = _is_simple_if_return(stmt)
    if return_stmt is None:
        return None

    if not _is_literal_false(return_stmt.value):
        return None

    return cast(ast.If, stmt)


def _get_stmt_index(func_body: list[ast.stmt], target: ast.stmt) -> int | None:
    """Find index of a statement in a function body.

    Args:
        func_body: List of statements in function body
        target: Statement to find

    Returns:
        Index if found, None otherwise
    """
    for i, stmt in enumerate(func_body):
        if stmt is target:
            return i
    return None


def _is_next_stmt_return_false(func_body: list[ast.stmt], for_index: int) -> bool:
    """Check if the next statement after for loop is return False.

    Args:
        func_body: List of statements in function body
        for_index: Index of the for loop

    Returns:
        True if next statement is return False
    """
    stmt = ast_utils.get_next_return_stmt(func_body, for_index)
    if stmt is None:
        return False
    return _is_literal_false(stmt.value)


def _is_next_stmt_return_true(func_body: list[ast.stmt], for_index: int) -> bool:
    """Check if the next statement after for loop is return True.

    Args:
        func_body: List of statements in function body
        for_index: Index of the for loop

    Returns:
        True if next statement is return True
    """
    stmt = ast_utils.get_next_return_stmt(func_body, for_index)
    if stmt is None:
        return False
    return _is_literal_true(stmt.value)


def _is_literal_true(node: ast.expr | None) -> bool:
    """Check if expression is literal True.

    Args:
        node: AST expression node

    Returns:
        True if node is literal True
    """
    if node is None:
        return False
    if isinstance(node, ast.Constant):
        return node.value is True
    return False


def _is_literal_false(node: ast.expr | None) -> bool:
    """Check if expression is literal False.

    Args:
        node: AST expression node

    Returns:
        True if node is literal False
    """
    if node is None:
        return False
    if isinstance(node, ast.Constant):
        return node.value is False
    return False


def _invert_condition(node: ast.expr) -> ast.expr:
    """Invert a boolean condition.

    If condition is 'not x', returns 'x'.
    Otherwise wraps in 'not (...)'.

    Args:
        node: AST expression to invert

    Returns:
        Inverted expression
    """
    # If already negated with 'not', unwrap it
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
        return node.operand

    # Otherwise wrap in 'not'
    return ast.UnaryOp(op=ast.Not(), operand=node)

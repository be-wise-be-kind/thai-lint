"""
Purpose: Analyze continue guard patterns in for loops

Scope: Extract and validate if/continue patterns from loop bodies

Overview: Provides helper functions for analyzing continue guard patterns in for loop
    bodies. Handles extraction of sequential if/continue statements, validation of
    simple continue-only patterns, and detection of side effects in conditions.
    Separates pattern analysis logic from main detection for better maintainability.

Dependencies: ast module for Python AST processing

Exports: extract_continue_patterns, is_continue_only, has_side_effects, has_body_after_continues

Interfaces: Functions for analyzing continue patterns in AST structures

Implementation: AST-based pattern matching for continue guard identification
"""

import ast


def extract_continue_patterns(body: list[ast.stmt]) -> list[ast.If]:
    """Extract leading if statements that only contain continue.

    Args:
        body: List of statements in for loop body

    Returns:
        List of ast.If nodes that are continue guards
    """
    continues: list[ast.If] = []
    for stmt in body:
        if not isinstance(stmt, ast.If):
            break
        if not is_continue_only(stmt):
            break
        continues.append(stmt)
    return continues


def is_continue_only(if_node: ast.If) -> bool:
    """Check if an if statement only contains continue.

    Args:
        if_node: AST If node to check

    Returns:
        True if the if statement is a simple continue guard
    """
    if len(if_node.body) != 1:
        return False
    if not isinstance(if_node.body[0], ast.Continue):
        return False
    if if_node.orelse:
        return False
    return True


def has_side_effects(continues: list[ast.If]) -> bool:
    """Check if any condition has side effects.

    Args:
        continues: List of continue guard if statements

    Returns:
        True if any condition has side effects (e.g., walrus operator)
    """
    for if_node in continues:
        if _condition_has_side_effects(if_node.test):
            return True
    return False


def _condition_has_side_effects(node: ast.expr) -> bool:
    """Check if expression has side effects.

    Args:
        node: AST expression node to check

    Returns:
        True if expression has side effects
    """
    for child in ast.walk(node):
        if isinstance(child, ast.NamedExpr):
            return True
    return False


def has_body_after_continues(body: list[ast.stmt], num_continues: int) -> bool:
    """Check if there are statements after continue guards.

    Args:
        body: List of statements in for loop body
        num_continues: Number of continue guards detected

    Returns:
        True if there are statements after the continue guards
    """
    return len(body) > num_continues

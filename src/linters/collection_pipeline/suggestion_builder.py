"""
Purpose: Build refactoring suggestions for collection pipeline patterns

Scope: Generate code suggestions for converting embedded filtering to collection pipelines

Overview: Provides helper functions for generating refactoring suggestions when embedded
    filtering patterns are detected. Handles condition inversion (converting continue guard
    conditions to filter conditions), target name extraction, and suggestion string generation.
    Separates suggestion logic from pattern detection logic for better maintainability.

Dependencies: ast module for Python AST processing

Exports: build_suggestion, invert_condition, get_target_name

Interfaces: Functions for suggestion generation and condition transformation

Implementation: AST-based condition inversion and string formatting for suggestions
"""

import ast


def get_target_name(target: ast.expr) -> str:
    """Get the loop variable name from AST target.

    Args:
        target: AST expression for loop target

    Returns:
        String representation of the loop variable
    """
    if isinstance(target, ast.Name):
        return target.id
    return ast.unparse(target)


def invert_condition(condition: ast.expr) -> str:
    """Invert a condition (for if not x: continue -> if x).

    Args:
        condition: AST expression for the condition

    Returns:
        String representation of the inverted condition
    """
    if isinstance(condition, ast.UnaryOp) and isinstance(condition.op, ast.Not):
        return ast.unparse(condition.operand)
    return f"not ({ast.unparse(condition)})"


def build_suggestion(loop_var: str, iterable: str, conditions: list[str]) -> str:
    """Generate refactoring suggestion code snippet.

    Args:
        loop_var: Name of the loop variable
        iterable: Source representation of the iterable
        conditions: List of filter conditions (already inverted)

    Returns:
        Code suggestion for refactoring to generator expression
    """
    combined = " and ".join(conditions)
    return f"for {loop_var} in ({loop_var} for {loop_var} in {iterable} if {combined}):"

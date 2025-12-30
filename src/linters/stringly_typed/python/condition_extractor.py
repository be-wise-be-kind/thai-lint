"""
Purpose: Extract string comparisons from Python condition expressions

Scope: Parse BoolOp and Compare nodes to extract string equality patterns

Overview: Provides functions to extract string comparisons from condition expressions
    in Python AST. Handles simple comparisons, or-combined, and and-combined
    conditions. Updates a collector object with extracted variable names and
    string values. Separated from main detector to reduce complexity.

Dependencies: ast module, variable_extractor

Exports: extract_from_condition, is_simple_string_equality, get_string_constant

Interfaces: Functions for extracting string comparisons from AST nodes

Implementation: Recursive traversal of BoolOp nodes with Compare extraction

Suppressions:
    - type:ignore[attr-defined]: AST node attribute access varies by node type (value.value)
"""

import ast

from .variable_extractor import extract_variable_name


def extract_from_condition(
    test: ast.expr,
    collector: object,
) -> None:
    """Extract string comparisons from a condition expression.

    Handles simple comparisons, or-combined, and and-combined comparisons.

    Args:
        test: The test expression from an if/elif
        collector: Collector to accumulate results into (must have variable_name
                  and string_values attributes)
    """
    if isinstance(test, ast.BoolOp):
        _extract_from_bool_op(test, collector)
    elif isinstance(test, ast.Compare):
        _extract_from_compare(test, collector)


def _extract_from_bool_op(node: ast.BoolOp, collector: object) -> None:
    """Extract from BoolOp (And/Or combined comparisons).

    Args:
        node: BoolOp node
        collector: Collector to accumulate results into
    """
    for value in node.values:
        _handle_bool_op_value(value, collector)


def _handle_bool_op_value(value: ast.expr, collector: object) -> None:
    """Handle a single value from a BoolOp node.

    Args:
        value: Expression value from BoolOp
        collector: Collector to accumulate results into
    """
    if isinstance(value, ast.Compare):
        _extract_from_compare(value, collector)
    elif isinstance(value, ast.BoolOp):
        _extract_from_bool_op(value, collector)


def _extract_from_compare(node: ast.Compare, collector: object) -> None:
    """Extract string value from a Compare node with Eq/NotEq.

    Args:
        node: Compare node to analyze
        collector: Collector to accumulate results into
    """
    if not _is_simple_equality(node):
        return

    string_value = _get_string_constant(node)
    if string_value is None:
        return

    var_name = extract_variable_name(node.left)
    _update_collector(collector, var_name, string_value)


def _is_simple_equality(node: ast.Compare) -> bool:
    """Check if Compare is a simple equality with one operator.

    Args:
        node: Compare node to check

    Returns:
        True if it's a simple x == y or x != y comparison
    """
    if len(node.ops) != 1:
        return False
    return isinstance(node.ops[0], (ast.Eq, ast.NotEq))


def _get_string_constant(node: ast.Compare) -> str | None:
    """Get string constant from the right side of comparison.

    Args:
        node: Compare node to extract from

    Returns:
        String value if comparator is a string constant, None otherwise
    """
    comparator = node.comparators[0]
    if isinstance(comparator, ast.Constant) and isinstance(comparator.value, str):
        return comparator.value
    return None


def _update_collector(
    collector: object,
    var_name: str | None,
    string_value: str,
) -> None:
    """Update collector with extracted variable and value.

    Args:
        collector: Collector to update
        var_name: Variable name from comparison
        string_value: String value from comparison
    """
    if collector.variable_name is None:  # type: ignore[attr-defined]
        collector.variable_name = var_name  # type: ignore[attr-defined]
    # Only add if same variable (or no variable tracking)
    if collector.variable_name == var_name or var_name is None:  # type: ignore[attr-defined]
        collector.string_values.add(string_value)  # type: ignore[attr-defined]

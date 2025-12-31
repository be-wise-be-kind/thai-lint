"""
Purpose: Analyze filter-map and takewhile anti-patterns in for loops

Scope: Extract and validate loops that build lists with transform/filter or takewhile

Overview: Provides helper functions for analyzing loops that initialize an empty list,
    iterate with a transform and conditional append, then return the list. Detects
    patterns like 'result=[]; for x: y=f(x); if y: result.append(y); return result'
    which can be refactored to list comprehensions with walrus operator. Also handles
    takewhile patterns with break statements.

Dependencies: ast module for Python AST processing

Exports: extract_filter_map_pattern, extract_takewhile_pattern, FilterMapMatch, TakewhileMatch

Interfaces: Functions for analyzing filter-map/takewhile patterns in AST function bodies

Implementation: AST-based pattern matching for filter-map/takewhile pattern identification
"""

import ast
from dataclasses import dataclass

from . import ast_utils


@dataclass
class FilterMapMatch:
    """Information about a detected filter-map pattern."""

    for_node: ast.For
    """The for loop AST node."""

    result_var: str
    """Name of the result list variable."""

    transform_var: str
    """Name of the variable holding transform result."""

    transform_expr: str
    """The transform expression as string."""


@dataclass
class TakewhileMatch:
    """Information about a detected takewhile pattern."""

    for_node: ast.For
    """The for loop AST node."""

    result_var: str
    """Name of the result list variable."""

    condition: ast.expr
    """The condition expression (inverted from break condition)."""


def extract_filter_map_pattern(
    func_body: list[ast.stmt], for_node: ast.For
) -> FilterMapMatch | None:
    """Extract filter-map pattern from a for loop in a function body.

    Pattern: result=[]; for x: y=f(x); if y: result.append(y); return result

    Args:
        func_body: List of statements in the function body
        for_node: The for loop AST node to analyze

    Returns:
        FilterMapMatch if pattern detected, None otherwise
    """
    # Find the for loop position
    for_index = _get_stmt_index(func_body, for_node)
    if for_index is None:
        return None

    # Find result list initialization before the loop
    result_init = _find_result_init_before(func_body, for_index)
    if result_init is None:
        return None

    result_var, _ = result_init

    # Check loop body has: assign, if, append pattern
    loop_pattern = _extract_assign_if_append(for_node.body, result_var)
    if loop_pattern is None:
        return None

    transform_var, transform_expr = loop_pattern

    # Check return result after loop
    if not _is_return_var_after(func_body, for_index, result_var):
        return None

    return FilterMapMatch(
        for_node=for_node,
        result_var=result_var,
        transform_var=transform_var,
        transform_expr=transform_expr,
    )


def extract_takewhile_pattern(
    func_body: list[ast.stmt], for_node: ast.For
) -> TakewhileMatch | None:
    """Extract takewhile pattern from a for loop in a function body.

    Pattern: result=[]; for x: if not cond: break; result.append(x); return result

    Args:
        func_body: List of statements in the function body
        for_node: The for loop AST node to analyze

    Returns:
        TakewhileMatch if pattern detected, None otherwise
    """
    # Find the for loop position
    for_index = _get_stmt_index(func_body, for_node)
    if for_index is None:
        return None

    # Find result list initialization before the loop
    result_init = _find_result_init_before(func_body, for_index)
    if result_init is None:
        return None

    result_var, _ = result_init

    # Check loop body has: if break, append pattern
    loop_pattern = _extract_if_break_append(for_node.body, result_var)
    if loop_pattern is None:
        return None

    condition = loop_pattern

    # Check return result after loop
    if not _is_return_var_after(func_body, for_index, result_var):
        return None

    return TakewhileMatch(
        for_node=for_node,
        result_var=result_var,
        condition=condition,
    )


def _get_stmt_index(func_body: list[ast.stmt], target: ast.stmt) -> int | None:
    """Find index of a statement in a function body."""
    for i, stmt in enumerate(func_body):
        if stmt is target:
            return i
    return None


def _get_assign_empty_list_var(stmt: ast.Assign) -> str | None:
    """Get variable name from simple assignment to empty list."""
    if len(stmt.targets) != 1:
        return None
    if not isinstance(stmt.targets[0], ast.Name):
        return None
    if not _is_empty_list(stmt.value):
        return None
    return stmt.targets[0].id


def _get_annassign_empty_list_var(stmt: ast.AnnAssign) -> str | None:
    """Get variable name from annotated assignment to empty list."""
    if not isinstance(stmt.target, ast.Name):
        return None
    if stmt.value is None:
        return None
    if not _is_empty_list(stmt.value):
        return None
    return stmt.target.id


def _get_empty_list_var(stmt: ast.stmt) -> str | None:
    """Get variable name if statement is empty list initialization.

    Handles both: result = [] and result: list[T] = []

    Args:
        stmt: Statement to check

    Returns:
        Variable name if empty list init, None otherwise
    """
    if isinstance(stmt, ast.Assign):
        return _get_assign_empty_list_var(stmt)
    if isinstance(stmt, ast.AnnAssign):
        return _get_annassign_empty_list_var(stmt)
    return None


def _find_result_init_before(func_body: list[ast.stmt], for_index: int) -> tuple[str, int] | None:
    """Find empty list initialization before the for loop.

    Searches backwards from for_index to find: result = [] or result: list[T] = []

    Args:
        func_body: List of statements in function body
        for_index: Index of the for loop

    Returns:
        Tuple of (variable_name, init_index) if found, None otherwise
    """
    for i in range(for_index - 1, -1, -1):
        var_name = _get_empty_list_var(func_body[i])
        if var_name is not None:
            return (var_name, i)
    return None


def _is_empty_list(node: ast.expr) -> bool:
    """Check if expression is an empty list literal."""
    return isinstance(node, ast.List) and len(node.elts) == 0


def _extract_simple_assignment(stmt: ast.stmt) -> tuple[str, str] | None:
    """Extract variable and expression from a simple assignment.

    Args:
        stmt: Statement to check

    Returns:
        Tuple of (var_name, expr_string) if simple assignment, None otherwise
    """
    if not isinstance(stmt, ast.Assign):
        return None
    if len(stmt.targets) != 1:
        return None
    if not isinstance(stmt.targets[0], ast.Name):
        return None
    return (stmt.targets[0].id, ast.unparse(stmt.value))


def _is_conditional_append(
    if_stmt: ast.If, condition_var: str, result_var: str, appended_var: str
) -> bool:
    """Check if statement is: if condition_var: result.append(appended_var).

    Args:
        if_stmt: The if statement to check
        condition_var: Expected condition variable name
        result_var: Expected result list name
        appended_var: Expected appended variable name

    Returns:
        True if pattern matches
    """
    if if_stmt.orelse:
        return False
    if not isinstance(if_stmt.test, ast.Name):
        return False
    if if_stmt.test.id != condition_var:
        return False
    if len(if_stmt.body) != 1:
        return False
    return _is_append_call(if_stmt.body[0], result_var, appended_var)


def _extract_assign_if_append(body: list[ast.stmt], result_var: str) -> tuple[str, str] | None:
    """Extract assign, if, append pattern from loop body.

    Pattern: y = f(x); if y: result.append(y)

    Args:
        body: List of statements in for loop body
        result_var: Name of the result list variable

    Returns:
        Tuple of (transform_var, transform_expr) if pattern matches, None otherwise
    """
    if len(body) != 2:
        return None

    # First statement should be assignment
    assignment = _extract_simple_assignment(body[0])
    if assignment is None:
        return None

    transform_var, transform_expr = assignment

    # Second statement should be: if transform_var: result.append(transform_var)
    if not isinstance(body[1], ast.If):
        return None

    if not _is_conditional_append(body[1], transform_var, result_var, transform_var):
        return None

    return (transform_var, transform_expr)


def _is_simple_if_break(stmt: ast.stmt) -> ast.If | None:
    """Check if statement is simple 'if cond: break' with no else.

    Args:
        stmt: Statement to check

    Returns:
        The if statement if pattern matches, None otherwise
    """
    if not isinstance(stmt, ast.If):
        return None
    if stmt.orelse:
        return None
    if len(stmt.body) != 1:
        return None
    if not isinstance(stmt.body[0], ast.Break):
        return None
    return stmt


def _extract_if_break_append(body: list[ast.stmt], result_var: str) -> ast.expr | None:
    """Extract if break, append pattern from loop body.

    Pattern: if not cond: break; result.append(x)

    Args:
        body: List of statements in for loop body
        result_var: Name of the result list variable

    Returns:
        The condition (inverted for takewhile) if pattern matches, None otherwise
    """
    if len(body) != 2:
        return None

    if_stmt = _is_simple_if_break(body[0])
    if if_stmt is None:
        return None

    if not isinstance(body[1], ast.Expr):
        return None

    return _invert_condition(if_stmt.test)


def _get_method_call_info(stmt: ast.stmt) -> tuple[str, str, list[ast.expr]] | None:
    """Extract method call info from statement: obj.method(args).

    Args:
        stmt: Statement to check

    Returns:
        Tuple of (object_name, method_name, args) if method call, None otherwise
    """
    if not isinstance(stmt, ast.Expr):
        return None
    if not isinstance(stmt.value, ast.Call):
        return None
    call = stmt.value
    if not isinstance(call.func, ast.Attribute):
        return None
    if not isinstance(call.func.value, ast.Name):
        return None
    return (call.func.value.id, call.func.attr, call.args)


def _is_single_name_arg(args: list[ast.expr], expected_name: str) -> bool:
    """Check if args list is single Name with expected id."""
    if len(args) != 1:
        return False
    if not isinstance(args[0], ast.Name):
        return False
    return args[0].id == expected_name


def _is_append_call(stmt: ast.stmt, result_var: str, appended_var: str) -> bool:
    """Check if statement is result.append(appended_var)."""
    info = _get_method_call_info(stmt)
    if info is None:
        return False
    obj_name, method_name, args = info
    if obj_name != result_var or method_name != "append":
        return False
    return _is_single_name_arg(args, appended_var)


def _is_return_var_after(func_body: list[ast.stmt], for_index: int, var_name: str) -> bool:
    """Check if the next statement after for loop is return var_name."""
    stmt = ast_utils.get_next_return_stmt(func_body, for_index)
    if stmt is None:
        return False

    if stmt.value is None:
        return False
    if not isinstance(stmt.value, ast.Name):
        return False

    return stmt.value.id == var_name


def _invert_condition(node: ast.expr) -> ast.expr:
    """Invert a boolean condition.

    If condition is 'not x', returns 'x'.
    Otherwise wraps in 'not (...)'.
    """
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
        return node.operand
    return ast.UnaryOp(op=ast.Not(), operand=node)

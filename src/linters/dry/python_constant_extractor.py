"""
Purpose: Extract Python module-level constants using AST parsing

Scope: Python constant extraction for duplicate constants detection

Overview: Extracts module-level constant definitions from Python source code using the AST module.
    Identifies constants as module-level assignments where the target name matches the ALL_CAPS
    naming convention (e.g., API_TIMEOUT = 30). Excludes private constants (leading underscore),
    class-level constants, and function-level constants to focus on public module constants that
    should be consolidated across files.

Dependencies: Python ast module, re for pattern matching, ConstantInfo from constant module

Exports: extract_python_constants function

Interfaces: extract_python_constants(content: str) -> list[ConstantInfo]

Implementation: AST-based parsing with module-level filtering and ALL_CAPS regex matching
"""

import ast

from .constant import CONSTANT_NAME_PATTERN, ConstantInfo

# Container types with fixed representations
CONTAINER_REPRESENTATIONS = {ast.List: "[...]", ast.Dict: "{...}", ast.Tuple: "(...)"}


def extract_python_constants(content: str) -> list[ConstantInfo]:
    """Extract constants from Python source code.

    Args:
        content: Python source code as string

    Returns:
        List of ConstantInfo for module-level constants
    """
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return []
    constants: list[ConstantInfo] = []
    for node in tree.body:
        constants.extend(_extract_from_node(node))
    return constants


def _extract_from_node(node: ast.stmt) -> list[ConstantInfo]:
    """Extract constants from a single AST node."""
    if isinstance(node, ast.Assign):
        return _extract_from_assign(node)
    if isinstance(node, ast.AnnAssign):
        return _extract_from_ann_assign(node)
    return []


def _extract_from_assign(node: ast.Assign) -> list[ConstantInfo]:
    """Extract constants from a simple assignment."""
    return [info for t in node.targets if (info := _to_const_info(t, node.value, node.lineno))]


def _extract_from_ann_assign(node: ast.AnnAssign) -> list[ConstantInfo]:
    """Extract constants from an annotated assignment."""
    if node.value is None:
        return []
    info = _to_const_info(node.target, node.value, node.lineno)
    return [info] if info else []


def _to_const_info(target: ast.expr, value: ast.expr, lineno: int) -> ConstantInfo | None:
    """Extract constant info from target and value."""
    if not isinstance(target, ast.Name):
        return None
    name = target.id
    if not _is_constant_name(name):
        return None
    return ConstantInfo(name=name, line_number=lineno, value=_get_value_string(value))


def _is_constant_name(name: str) -> bool:
    """Check if name matches constant naming convention."""
    return not name.startswith("_") and bool(CONSTANT_NAME_PATTERN.match(name))


def _get_value_string(value: ast.expr) -> str | None:
    """Get string representation of a value expression."""
    if isinstance(value, ast.Constant):
        return repr(value.value)
    if isinstance(value, ast.Name):
        return value.id
    if isinstance(value, ast.Call):
        return _call_to_string(value)
    return CONTAINER_REPRESENTATIONS.get(type(value))


def _call_to_string(node: ast.Call) -> str:
    """Convert call expression to string."""
    if isinstance(node.func, ast.Name):
        return f"{node.func.id}(...)"
    return "call(...)"

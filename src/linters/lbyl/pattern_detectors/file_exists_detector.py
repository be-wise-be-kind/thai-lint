"""
Purpose: AST-based detector for file exists LBYL patterns

Scope: Detects 'if os.path.exists(f): open(f)' and 'if Path(f).exists(): open(f)' patterns

Overview: Provides FileExistsDetector class that uses AST traversal to find LBYL anti-patterns
    involving file existence checking. Identifies patterns where code checks if a file exists
    before opening it. Handles both os.path.exists and pathlib.Path.exists patterns, including
    import aliases. Returns FileExistsPattern objects containing the file path expression and
    location. Avoids false positives for directory checks and different file paths.

Dependencies: ast module, base detector classes from pattern_detectors.base

Exports: FileExistsPattern, FileExistsDetector

Interfaces: FileExistsDetector.find_patterns(tree: ast.AST) -> list[FileExistsPattern]

Implementation: AST NodeVisitor pattern with visit_If to detect exists check followed by
    file operation (open, read_text, write_text)

Suppressions:
    - N802: visit_If follows Python AST visitor naming convention (camelCase required)
    - invalid-name: visit_If follows Python AST visitor naming convention (camelCase required)
"""

import ast
from dataclasses import dataclass

from .base import BaseLBYLDetector, LBYLPattern


@dataclass
class FileExistsPattern(LBYLPattern):
    """Pattern data for file exists LBYL anti-pattern."""

    file_path_expression: str
    check_type: str  # "os.path.exists", "Path.exists", "exists"


# File operation methods on Path objects
_PATH_FILE_METHODS = frozenset(("read_text", "write_text", "read_bytes", "write_bytes"))


def _is_exists_attribute_call(node: ast.Call) -> bool:
    """Check if node is a method call to .exists() with one argument."""
    if not isinstance(node.func, ast.Attribute):
        return False
    return node.func.attr == "exists" and len(node.args) == 1


def _get_os_path_check_type(
    func_value: ast.expr, path_arg: ast.expr
) -> tuple[ast.expr | None, str | None]:
    """Get check type for os.path.exists or alias.exists pattern."""
    if isinstance(func_value, ast.Attribute) and func_value.attr == "path":
        return path_arg, "os.path.exists"
    if isinstance(func_value, ast.Name):
        return path_arg, f"{func_value.id}.exists"
    return None, None


def _check_os_path_exists_attribute(node: ast.Call) -> tuple[ast.expr | None, str | None]:
    """Check for os.path.exists(f) or alias.exists(f) pattern."""
    if not _is_exists_attribute_call(node):
        return None, None
    func = node.func
    if not isinstance(func, ast.Attribute):
        return None, None
    return _get_os_path_check_type(func.value, node.args[0])


def _check_exists_name_call(node: ast.Call) -> tuple[ast.expr | None, str | None]:
    """Check for exists(f) pattern from 'from os.path import exists'."""
    if isinstance(node.func, ast.Name) and node.func.id == "exists" and len(node.args) == 1:
        return node.args[0], "exists"
    return None, None


def _is_os_path_exists_call(node: ast.expr) -> tuple[ast.expr | None, str | None]:
    """Check if node is os.path.exists(f) or exists(f) call."""
    if not isinstance(node, ast.Call):
        return None, None

    result = _check_os_path_exists_attribute(node)
    if result[0] is not None:
        return result
    return _check_exists_name_call(node)


def _is_os_path_attribute(node: ast.expr) -> bool:
    """Check if node is an os.path attribute access."""
    return isinstance(node, ast.Attribute) and node.attr == "path"


def _check_path_constructor_exists(func_value: ast.expr) -> tuple[ast.expr | None, str | None]:
    """Check for Path(f).exists() pattern."""
    if not isinstance(func_value, ast.Call):
        return None, None
    if not isinstance(func_value.func, ast.Name) or func_value.func.id != "Path":
        return None, None
    if len(func_value.args) == 1:
        return func_value.args[0], "Path.exists"
    return None, None


def _check_variable_exists(func_value: ast.expr) -> tuple[ast.expr | None, str | None]:
    """Check for p.exists() or self.path.exists() pattern."""
    if isinstance(func_value, (ast.Name, ast.Attribute)):
        return func_value, "Path.exists"
    return None, None


def _is_pathlib_exists_method(node: ast.expr) -> bool:
    """Check if node is a .exists() method call (not os.path.exists)."""
    if not isinstance(node, ast.Call):
        return False
    if not isinstance(node.func, ast.Attribute) or node.func.attr != "exists":
        return False
    return not _is_os_path_attribute(node.func.value)


def _extract_pathlib_func_value(node: ast.expr) -> ast.expr | None:
    """Extract func value from pathlib .exists() call, or None."""
    if not _is_pathlib_exists_method(node):
        return None
    # After _is_pathlib_exists_method, we know node is Call with Attribute func
    if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
        return None
    return node.func.value


def _is_pathlib_exists_call(node: ast.expr) -> tuple[ast.expr | None, str | None]:
    """Check if node is Path(f).exists() or p.exists() call."""
    func_value = _extract_pathlib_func_value(node)
    if func_value is None:
        return None, None

    result = _check_path_constructor_exists(func_value)
    if result[0] is not None:
        return result
    return _check_variable_exists(func_value)


def _try_extract_exists_call(node: ast.expr) -> tuple[ast.expr | None, str | None]:
    """Try to extract file exists call arguments."""
    result = _is_os_path_exists_call(node)
    if result[0] is not None:
        return result
    return _is_pathlib_exists_call(node)


def _is_open_call(node: ast.Call, expected_path: str) -> bool:
    """Check if node is open(path) call."""
    if not isinstance(node.func, ast.Name) or node.func.id != "open":
        return False
    return len(node.args) >= 1 and ast.dump(node.args[0]) == expected_path


def _is_path_method_call(node: ast.Call, expected_path: str) -> bool:
    """Check if node is path.read_text() or similar method call."""
    if not isinstance(node.func, ast.Attribute):
        return False
    if node.func.attr not in _PATH_FILE_METHODS:
        return False
    return ast.dump(node.func.value) == expected_path


def _is_file_operation(node: ast.AST, expected_path: str) -> bool:
    """Check if node is a file operation on the expected path."""
    if not isinstance(node, ast.Call):
        return False
    return _is_open_call(node, expected_path) or _is_path_method_call(node, expected_path)


def _is_inverted_check(test: ast.expr) -> bool:
    """Check if test is 'not exists(f)' pattern."""
    return isinstance(test, ast.UnaryOp) and isinstance(test.op, ast.Not)


class FileExistsDetector(BaseLBYLDetector[FileExistsPattern]):
    """Detects 'if exists(f): open(f)' LBYL patterns."""

    def __init__(self) -> None:
        """Initialize the detector."""
        self._patterns: list[FileExistsPattern] = []

    def visit_If(self, node: ast.If) -> None:  # noqa: N802  # pylint: disable=invalid-name
        """Visit if statement to check for file exists LBYL pattern."""
        self._check_file_exists_pattern(node)
        self.generic_visit(node)

    def _check_file_exists_pattern(self, node: ast.If) -> None:
        """Check if node matches file exists LBYL pattern."""
        if _is_inverted_check(node.test):
            return

        path_expr, check_type = _try_extract_exists_call(node.test)
        if path_expr is None or check_type is None:
            return

        if self._body_has_file_operation(node.body, path_expr):
            self._patterns.append(self._create_pattern(node, path_expr, check_type))

    def _body_has_file_operation(self, body: list[ast.stmt], path_expr: ast.expr) -> bool:
        """Check if body contains file operation on the same path."""
        expected_path = ast.dump(path_expr)
        return any(
            _is_file_operation(node, expected_path) for stmt in body for node in ast.walk(stmt)
        )

    def _create_pattern(
        self, node: ast.If, path_expr: ast.expr, check_type: str
    ) -> FileExistsPattern:
        """Create FileExistsPattern from detected pattern."""
        return FileExistsPattern(
            line_number=node.lineno,
            column=node.col_offset,
            file_path_expression=ast.unparse(path_expr),
            check_type=check_type,
        )

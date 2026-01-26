"""
Purpose: Detect constant definition files that should be exempt from magic number checking

Scope: File-level detection of definition patterns (status codes, constants files)

Overview: Provides functions to detect if a file is a constant definition file that should
    be exempt from magic number violations. Definition files exist specifically to define
    named constants and shouldn't be flagged. Detection is based on:
    1. Filename patterns (*_codes.py, *_constants.py, constants.py)
    2. Content patterns (dicts with 5+ int keys, 10+ UPPERCASE constant assignments)
    Files matching these patterns contain legitimate constant definitions.

Dependencies: ast module for parsing, pathlib for Path handling, re for pattern matching

Exports: is_definition_file function

Interfaces: is_definition_file(file_path, content) -> bool

Implementation: Filename pattern matching and AST-based content analysis
"""

import ast
import re
from pathlib import Path

# Threshold for number of UPPERCASE constants to consider a file as definition file
MIN_UPPERCASE_CONSTANTS = 10

# Threshold for number of int keys in a dict to consider it a definition pattern
MIN_DICT_INT_KEYS = 5


def is_definition_file(file_path: Path | str | None, content: str | None) -> bool:
    """Check if file is a constant definition file that should be exempt.

    Args:
        file_path: Path to the file
        content: File content

    Returns:
        True if file is a definition file that should be exempt
    """
    if _matches_definition_filename(file_path):
        return True

    if content and _has_definition_content_patterns(content):
        return True

    return False


def _matches_definition_filename(file_path: Path | str | None) -> bool:
    """Check if filename matches definition file patterns.

    Patterns:
    - *_codes.py (status_codes.py, error_codes.py, etc.)
    - *_constants.py (app_constants.py, etc.)
    - constants.py

    Args:
        file_path: Path to the file

    Returns:
        True if filename matches definition patterns
    """
    if not file_path:
        return False

    file_name = Path(file_path).name.lower()

    # Check for *_codes.py pattern
    if file_name.endswith("_codes.py"):
        return True

    # Check for constants.py or *_constants.py
    if file_name == "constants.py" or file_name.endswith("_constants.py"):
        return True

    return False


def _has_definition_content_patterns(content: str) -> bool:
    """Check if content has definition file patterns.

    Patterns:
    - 10+ UPPERCASE constant assignments
    - Dict with 5+ integer keys

    Args:
        content: File content

    Returns:
        True if content matches definition patterns
    """
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return False

    # Check for many UPPERCASE constants
    if _count_uppercase_constants(tree) >= MIN_UPPERCASE_CONSTANTS:
        return True

    # Check for dicts with many int keys
    if _has_dict_with_int_keys(tree):
        return True

    return False


def _count_uppercase_constants(tree: ast.Module) -> int:
    """Count UPPERCASE constant assignments at module level.

    Args:
        tree: Parsed AST module

    Returns:
        Number of UPPERCASE constant assignments
    """
    count = 0
    for node in tree.body:
        if isinstance(node, ast.Assign):
            count += _count_numeric_constant_targets(node)
    return count


def _count_numeric_constant_targets(assign_node: ast.Assign) -> int:
    """Count UPPERCASE constant targets with numeric values in an assignment.

    Args:
        assign_node: AST Assign node

    Returns:
        Number of uppercase constant targets with numeric values
    """
    if not _is_numeric_constant(assign_node.value):
        return 0
    return sum(1 for t in assign_node.targets if _is_uppercase_name_target(t))


def _is_numeric_constant(value: ast.expr) -> bool:
    """Check if value is a numeric constant.

    Args:
        value: AST expression node

    Returns:
        True if value is a numeric constant
    """
    return isinstance(value, ast.Constant) and isinstance(value.value, (int, float))


def _is_uppercase_name_target(target: ast.expr) -> bool:
    """Check if target is an uppercase name.

    Args:
        target: AST expression node

    Returns:
        True if target is an uppercase Name node
    """
    return isinstance(target, ast.Name) and _is_constant_name(target.id)


def _is_constant_name(name: str) -> bool:
    """Check if name follows UPPERCASE constant convention.

    Args:
        name: Variable name

    Returns:
        True if name is UPPERCASE (with underscores allowed)
    """
    # Must be uppercase and contain at least 2 characters
    if len(name) < 2:
        return False
    # Allow underscores but must have uppercase letters
    return re.match(r"^[A-Z][A-Z0-9_]*$", name) is not None


def _has_dict_with_int_keys(tree: ast.Module) -> bool:
    """Check if module has a dict with many integer keys.

    Args:
        tree: Parsed AST module

    Returns:
        True if there's a dict with MIN_DICT_INT_KEYS+ int keys
    """
    return any(_has_enough_int_keys(node) for node in ast.walk(tree) if isinstance(node, ast.Dict))


def _has_enough_int_keys(dict_node: ast.Dict) -> bool:
    """Check if dict has enough integer keys to be a definition pattern.

    Args:
        dict_node: AST Dict node

    Returns:
        True if dict has MIN_DICT_INT_KEYS or more integer keys
    """
    return _count_int_keys(dict_node) >= MIN_DICT_INT_KEYS


def _count_int_keys(dict_node: ast.Dict) -> int:
    """Count integer keys in a dict.

    Args:
        dict_node: AST Dict node

    Returns:
        Number of integer constant keys
    """
    return sum(1 for key in dict_node.keys if _is_int_key(key))


def _is_int_key(key: ast.expr | None) -> bool:
    """Check if key is an integer constant.

    Args:
        key: AST expression node (or None for **dict unpacking)

    Returns:
        True if key is an integer constant
    """
    return isinstance(key, ast.Constant) and isinstance(key.value, int)

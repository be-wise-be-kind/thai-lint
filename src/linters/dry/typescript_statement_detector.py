"""
Purpose: Detects single-statement patterns in TypeScript/JavaScript code for DRY linter filtering

Scope: Tree-sitter AST analysis to identify single logical statements that should not be flagged

Overview: Provides sophisticated single-statement pattern detection to filter false positives in the
    DRY linter for TypeScript/JavaScript code. Uses tree-sitter AST to identify when a code block
    represents a single logical statement (decorators, call expressions, object literals, class fields,
    JSX elements, interface definitions) that should not be flagged as duplicate code.

Dependencies: tree-sitter for TypeScript AST parsing

Exports: is_single_statement, should_include_block functions

Interfaces: is_single_statement(content, start_line, end_line) -> bool,
    should_include_block(content, start_line, end_line) -> bool

Implementation: Tree-sitter AST walking with pattern matching for TypeScript constructs

Suppressions:
    - type:ignore[assignment,misc]: Tree-sitter Node type alias (optional dependency fallback)
"""

from collections.abc import Generator
from typing import Any

from src.analyzers.typescript_base import TREE_SITTER_AVAILABLE

if TREE_SITTER_AVAILABLE:
    from tree_sitter import Node
else:
    Node = Any  # type: ignore[assignment,misc]


def is_single_statement(content: str, start_line: int, end_line: int) -> bool:
    """Check if a line range is a single logical statement.

    Args:
        content: TypeScript source code
        start_line: Starting line number (1-indexed)
        end_line: Ending line number (1-indexed)

    Returns:
        True if this range represents a single logical statement/expression
    """
    if not TREE_SITTER_AVAILABLE:
        return False

    from src.analyzers.typescript_base import TypeScriptBaseAnalyzer

    analyzer = TypeScriptBaseAnalyzer()
    root = analyzer.parse_typescript(content)
    if not root:
        return False

    return _check_overlapping_nodes(root, start_line, end_line)


def should_include_block(content: str, start_line: int, end_line: int) -> bool:
    """Check if block should be included (not overlapping interface definitions).

    Args:
        content: File content
        start_line: Block start line
        end_line: Block end line

    Returns:
        False if block overlaps interface definition, True otherwise
    """
    interface_ranges = _find_interface_ranges(content)
    return not _overlaps_interface(start_line, end_line, interface_ranges)


def _check_overlapping_nodes(root: Node, start_line: int, end_line: int) -> bool:
    """Check if any AST node overlaps and matches single-statement pattern."""
    ts_start = start_line - 1  # Convert to 0-indexed
    ts_end = end_line - 1

    return any(_node_overlaps_and_matches(node, ts_start, ts_end) for node in _walk_nodes(root))


def _walk_nodes(node: Node) -> Generator[Node, None, None]:
    """Generator to walk all nodes in tree."""
    yield node
    for child in node.children:
        yield from _walk_nodes(child)


def _node_overlaps_and_matches(node: Node, ts_start: int, ts_end: int) -> bool:
    """Check if node overlaps with range and matches single-statement pattern."""
    node_start = node.start_point[0]
    node_end = node.end_point[0]

    overlaps = not (node_end < ts_start or node_start > ts_end)
    if not overlaps:
        return False

    return _is_single_statement_pattern(node, ts_start, ts_end)


def _is_single_statement_pattern(node: Node, ts_start: int, ts_end: int) -> bool:
    """Check if an AST node represents a single-statement pattern to filter."""
    node_start = node.start_point[0]
    node_end = node.end_point[0]
    contains = (node_start <= ts_start) and (node_end >= ts_end)

    matchers = [
        _matches_simple_container_pattern(node, contains),
        _matches_call_expression_pattern(node, ts_start, ts_end, contains),
        _matches_declaration_pattern(node, contains),
        _matches_jsx_pattern(node, contains),
        _matches_class_body_pattern(node, ts_start, ts_end),
    ]
    return any(matchers)


def _matches_simple_container_pattern(node: Node, contains: bool) -> bool:
    """Check if node is a simple container pattern (decorator, object, etc.)."""
    simple_types = (
        "decorator",
        "object",
        "member_expression",
        "as_expression",
        "array_pattern",
    )
    return node.type in simple_types and contains


def _matches_call_expression_pattern(
    node: Node, ts_start: int, ts_end: int, contains: bool
) -> bool:
    """Check if node is a call expression pattern."""
    if node.type != "call_expression":
        return False

    node_start = node.start_point[0]
    node_end = node.end_point[0]
    is_multiline = node_start < node_end
    if is_multiline and node_start <= ts_start <= node_end:
        return True

    return contains


def _matches_declaration_pattern(node: Node, contains: bool) -> bool:
    """Check if node is a lexical declaration pattern."""
    if node.type != "lexical_declaration" or not contains:
        return False

    if _contains_function_body(node):
        return False

    return True


def _matches_jsx_pattern(node: Node, contains: bool) -> bool:
    """Check if node is a JSX element pattern."""
    jsx_types = ("jsx_opening_element", "jsx_self_closing_element")
    return node.type in jsx_types and contains


def _matches_class_body_pattern(node: Node, ts_start: int, ts_end: int) -> bool:
    """Check if node is a class body field definition pattern."""
    if node.type != "class_body":
        return False

    return _is_in_class_field_area(node, ts_start, ts_end)


def _contains_function_body(node: Node) -> bool:
    """Check if node contains an arrow function or function expression."""
    for child in node.children:
        if child.type in ("arrow_function", "function", "function_expression"):
            return True
        if _contains_function_body(child):
            return True
    return False


def _find_first_method_line(class_body: Node) -> int | None:
    """Find line number of first method in class body."""
    for child in class_body.children:
        if child.type in ("method_definition", "function_declaration"):
            return child.start_point[0]
    return None


def _is_in_class_field_area(class_body: Node, ts_start: int, ts_end: int) -> bool:
    """Check if range is in class field definition area (before methods)."""
    first_method_line = _find_first_method_line(class_body)
    class_start = class_body.start_point[0]
    class_end = class_body.end_point[0]

    if first_method_line is None:
        return class_start <= ts_start and class_end >= ts_end

    return class_start <= ts_start and ts_end < first_method_line


def _find_interface_ranges(content: str) -> list[tuple[int, int]]:
    """Find line ranges of interface/type definitions."""
    ranges: list[tuple[int, int]] = []
    lines = content.split("\n")
    state = {"in_interface": False, "start_line": 0, "brace_count": 0}

    for i, line in enumerate(lines, start=1):
        stripped = line.strip()
        _process_line_for_interface(stripped, i, state, ranges)

    return ranges


def _process_line_for_interface(
    stripped: str, line_num: int, state: dict[str, Any], ranges: list[tuple[int, int]]
) -> None:
    """Process single line for interface detection."""
    if _is_interface_start(stripped):
        _handle_interface_start(stripped, line_num, state, ranges)
        return

    if state["in_interface"]:
        _handle_interface_continuation(stripped, line_num, state, ranges)


def _is_interface_start(stripped: str) -> bool:
    """Check if line starts interface/type definition."""
    return stripped.startswith(("interface ", "type ")) and "{" in stripped


def _handle_interface_start(
    stripped: str, line_num: int, state: dict[str, Any], ranges: list[tuple[int, int]]
) -> None:
    """Handle start of interface definition."""
    state["in_interface"] = True
    state["start_line"] = line_num
    state["brace_count"] = stripped.count("{") - stripped.count("}")

    if state["brace_count"] == 0:
        ranges.append((line_num, line_num))
        state["in_interface"] = False


def _handle_interface_continuation(
    stripped: str, line_num: int, state: dict[str, Any], ranges: list[tuple[int, int]]
) -> None:
    """Handle continuation of interface definition."""
    state["brace_count"] += stripped.count("{") - stripped.count("}")
    if state["brace_count"] == 0:
        ranges.append((state["start_line"], line_num))
        state["in_interface"] = False


def _overlaps_interface(start: int, end: int, interface_ranges: list[tuple[int, int]]) -> bool:
    """Check if block overlaps with any interface range."""
    return any(start <= if_end and end >= if_start for if_start, if_end in interface_ranges)

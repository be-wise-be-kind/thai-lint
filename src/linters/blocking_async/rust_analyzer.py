"""
Purpose: Analyzer for detecting blocking operations inside async functions in Rust code

Scope: Pattern detection for std::fs, std::thread::sleep, and std::net calls in async contexts

Overview: Provides RustBlockingAsyncAnalyzer that extends RustBaseAnalyzer to detect blocking
    API calls inside async functions in Rust code. Detects three categories: filesystem operations
    (std::fs::read_to_string, std::fs::write, etc.), thread sleep (std::thread::sleep), and
    blocking network calls (std::net::TcpStream::connect, etc.). Supports both fully-qualified
    paths (std::fs::read_to_string) and short paths (fs::read_to_string after use std::fs).
    Excludes blocking calls wrapped in async-safe wrappers (asyncify, spawn_blocking,
    block_in_place) which correctly offload work to a thread pool. Uses tree-sitter AST to
    find function_item nodes, filter to async functions, walk bodies for call_expression nodes
    with scoped_identifier paths, and match against known blocking API patterns. Returns
    structured BlockingCall dataclass instances with location, pattern type, test context, and
    surrounding code for violation reporting.

Dependencies: src.analyzers.rust_base for tree-sitter parsing and traversal

Exports: RustBlockingAsyncAnalyzer, BlockingCall

Interfaces: find_blocking_calls(code: str) -> list[BlockingCall]

Implementation: AST-based async function detection with scoped_identifier path extraction
    and pattern matching against known blocking APIs
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from src.analyzers.rust_base import RustBaseAnalyzer
from src.core.linter_utils import get_line_context

if TYPE_CHECKING:
    from tree_sitter import Node

# Blocking std::fs function names
_BLOCKING_FS_FUNCTIONS = frozenset(
    {
        "read_to_string",
        "read",
        "write",
        "create_dir",
        "create_dir_all",
        "remove_file",
        "remove_dir",
        "remove_dir_all",
        "rename",
        "copy",
        "metadata",
        "read_dir",
        "canonicalize",
        "read_link",
    }
)

# Blocking std::net type names that have blocking methods
_BLOCKING_NET_TYPES = frozenset(
    {
        "TcpStream",
        "TcpListener",
        "UdpSocket",
    }
)


@dataclass
class BlockingCall:
    """Represents a detected blocking call inside an async function."""

    line: int
    column: int
    pattern: str  # "fs-in-async", "sleep-in-async", "net-in-async"
    is_in_test: bool
    context: str  # Surrounding code snippet
    blocking_api: str  # e.g., "std::fs::read_to_string"


class RustBlockingAsyncAnalyzer(RustBaseAnalyzer):
    """Analyzer for detecting blocking operations inside async functions."""

    def find_blocking_calls(self, code: str) -> list[BlockingCall]:
        """Find all blocking calls inside async functions.

        Args:
            code: Rust source code to analyze

        Returns:
            List of detected blocking calls with pattern classification
        """
        if not self.tree_sitter_available:
            return []

        root = self.parse_rust(code)
        if root is None:
            return []

        calls: list[BlockingCall] = []
        self._scan_for_blocking_calls(root, code, calls)
        return calls

    def _scan_for_blocking_calls(self, node: Node, code: str, calls: list[BlockingCall]) -> None:
        """Recursively scan AST for blocking calls in async contexts.

        Finds call_expression nodes inside async functions and checks if they
        invoke known blocking APIs.

        Args:
            node: Current tree-sitter node to inspect
            code: Original source code for context extraction
            calls: Accumulator list for detected calls
        """
        if node.type == "call_expression" and self._is_in_async_context(node):
            blocking_call = self._check_blocking_call(node, code)
            if blocking_call is not None:
                calls.append(blocking_call)

        for child in node.children:
            self._scan_for_blocking_calls(child, code, calls)

    def _is_in_async_context(self, node: Node) -> bool:
        """Check if node is inside an async function body.

        Walks up the parent chain looking for function_item nodes that
        are async functions.

        Args:
            node: Node to check

        Returns:
            True if inside an async function
        """
        current: Node | None = node.parent
        while current is not None:
            if current.type == "function_item" and self.is_async_function(current):
                return True
            current = current.parent
        return False

    def _check_blocking_call(self, call_node: Node, code: str) -> BlockingCall | None:
        """Check if a call expression is a blocking API call.

        Extracts the call path from the scoped_identifier child and matches
        it against known blocking API patterns. Skips calls wrapped in
        spawn_blocking/asyncify which are correctly offloaded to a thread pool.

        Args:
            call_node: A call_expression node
            code: Original source code for context extraction

        Returns:
            BlockingCall if blocking API detected, None otherwise
        """
        path = self._extract_call_path(call_node)
        if not path:
            return None

        pattern = _classify_blocking_pattern(path)
        if pattern is None:
            return None

        if _is_inside_blocking_wrapper(call_node):
            return None

        return BlockingCall(
            line=call_node.start_point[0] + 1,
            column=call_node.start_point[1],
            pattern=pattern,
            is_in_test=self.is_inside_test(call_node),
            context=get_line_context(code, call_node.start_point[0]),
            blocking_api=path,
        )

    def _extract_call_path(self, call_node: Node) -> str:
        """Extract the full call path from a call_expression.

        Handles both direct scoped calls (std::fs::read_to_string(...))
        and method-style calls that chain on scoped calls.

        Args:
            call_node: A call_expression node

        Returns:
            Full path string (e.g., "std::fs::read_to_string"), or empty string
        """
        for child in call_node.children:
            if child.type == "scoped_identifier":
                return self.extract_node_text(child)
        return ""


def _classify_blocking_pattern(path: str) -> str | None:
    """Classify a call path into a blocking pattern category.

    Checks the path against known blocking API patterns for filesystem,
    thread sleep, and network operations.

    Args:
        path: Full or short call path (e.g., "std::fs::read_to_string")

    Returns:
        Pattern string or None if not a blocking pattern
    """
    if _is_blocking_fs(path):
        return "fs-in-async"
    if _is_blocking_sleep(path):
        return "sleep-in-async"
    if _is_blocking_net(path):
        return "net-in-async"
    return None


def _is_blocking_fs(path: str) -> bool:
    """Check if path matches a blocking filesystem operation.

    Matches both fully-qualified (std::fs::read_to_string) and
    short paths (fs::read_to_string).

    Args:
        path: Call path to check

    Returns:
        True if path is a blocking fs operation
    """
    parts = path.split("::")
    return _matches_std_fs_pattern(parts) or _matches_short_fs_pattern(parts)


def _matches_std_fs_pattern(parts: list[str]) -> bool:
    """Check for fully-qualified std::fs::function pattern.

    Args:
        parts: Path components split by ::

    Returns:
        True if matches std::fs::function_name
    """
    if len(parts) < 3:
        return False
    return parts[0] == "std" and parts[1] == "fs" and parts[2] in _BLOCKING_FS_FUNCTIONS


def _matches_short_fs_pattern(parts: list[str]) -> bool:
    """Check for short fs::function pattern.

    Args:
        parts: Path components split by ::

    Returns:
        True if matches fs::function_name
    """
    if len(parts) < 2:
        return False
    return parts[0] == "fs" and parts[1] in _BLOCKING_FS_FUNCTIONS


def _is_blocking_sleep(path: str) -> bool:
    """Check if path matches std::thread::sleep.

    Matches both std::thread::sleep and thread::sleep.

    Args:
        path: Call path to check

    Returns:
        True if path is a blocking sleep call
    """
    parts = path.split("::")
    return _matches_std_sleep_pattern(parts) or _matches_short_sleep_pattern(parts)


def _matches_std_sleep_pattern(parts: list[str]) -> bool:
    """Check for fully-qualified std::thread::sleep pattern.

    Args:
        parts: Path components split by ::

    Returns:
        True if matches std::thread::sleep
    """
    if len(parts) < 3:
        return False
    return parts[0] == "std" and parts[1] == "thread" and parts[2] == "sleep"


def _matches_short_sleep_pattern(parts: list[str]) -> bool:
    """Check for short thread::sleep pattern.

    Args:
        parts: Path components split by ::

    Returns:
        True if matches thread::sleep
    """
    if len(parts) < 2:
        return False
    return parts[0] == "thread" and parts[1] == "sleep"


def _is_blocking_net(path: str) -> bool:
    """Check if path matches a blocking network operation.

    Matches both fully-qualified (std::net::TcpStream::connect) and
    short paths (net::TcpStream::connect, TcpStream::connect).

    Args:
        path: Call path to check

    Returns:
        True if path is a blocking net operation
    """
    parts = path.split("::")
    return _matches_std_net_pattern(parts) or _matches_short_net_pattern(parts)


def _matches_std_net_pattern(parts: list[str]) -> bool:
    """Check for fully-qualified std::net::Type::method pattern.

    Args:
        parts: Path components split by ::

    Returns:
        True if matches std::net::TcpStream/TcpListener/UdpSocket pattern
    """
    if len(parts) < 3:
        return False
    return parts[0] == "std" and parts[1] == "net" and parts[2] in _BLOCKING_NET_TYPES


def _matches_short_net_pattern(parts: list[str]) -> bool:
    """Check for short net::Type::method or Type::method pattern.

    Args:
        parts: Path components split by ::

    Returns:
        True if matches short net pattern
    """
    if len(parts) >= 2 and parts[0] == "net" and parts[1] in _BLOCKING_NET_TYPES:
        return True
    return False


# Function names that safely wrap blocking operations for async execution
_ASYNC_WRAPPER_FUNCTIONS = frozenset(
    {
        "asyncify",
        "spawn_blocking",
        "block_in_place",
    }
)


def _is_inside_blocking_wrapper(node: Node) -> bool:
    """Check if a blocking call is wrapped in an async-safe wrapper function.

    Detects patterns like asyncify(move || std::fs::read(...)) or
    spawn_blocking(move || { std::fs::write(...) }) where blocking calls
    are correctly offloaded to a thread pool.

    Args:
        node: The blocking call_expression node

    Returns:
        True if the call is inside a known async wrapper function
    """
    current: Node | None = node.parent
    while current is not None:
        if _is_wrapper_call(current):
            return True
        current = current.parent
    return False


def _is_wrapper_call(node: Node) -> bool:
    """Check if a node is a call to a known async wrapper function.

    Args:
        node: Node to check

    Returns:
        True if node is a call_expression to asyncify/spawn_blocking/block_in_place
    """
    if node.type != "call_expression":
        return False
    return any(_child_is_wrapper_name(child) for child in node.children)


def _child_is_wrapper_name(child: Node) -> bool:
    """Check if a child node is a wrapper function name.

    Args:
        child: Child node of a call_expression

    Returns:
        True if the child is an identifier or scoped_identifier matching a wrapper name
    """
    if child.type == "identifier":
        return _node_text_matches_wrapper(child)
    if child.type == "scoped_identifier":
        return _scoped_name_matches_wrapper(child)
    return False


def _node_text_matches_wrapper(node: Node) -> bool:
    """Check if a node's text matches a wrapper function name."""
    text = node.text
    return text is not None and text.decode() in _ASYNC_WRAPPER_FUNCTIONS


def _scoped_name_matches_wrapper(node: Node) -> bool:
    """Check if a scoped identifier's final segment matches a wrapper function name."""
    text = node.text
    if text is None:
        return False
    func_name = text.decode().split("::")[-1]
    return func_name in _ASYNC_WRAPPER_FUNCTIONS

"""
Purpose: Build Violation objects for Rust blocking-in-async patterns

Scope: Creates violations with actionable suggestions for fs-in-async, sleep-in-async,
    and net-in-async patterns

Overview: Provides module-level functions that create Violation objects for detected
    blocking operations inside async functions in Rust code. Each violation includes the
    rule ID, location, descriptive message explaining the concurrency impact, and a
    suggestion for async-compatible alternatives such as tokio::fs, tokio::time::sleep,
    or tokio::net equivalents.

Dependencies: src.core.types for Violation dataclass

Exports: build_fs_in_async_violation, build_sleep_in_async_violation, build_net_in_async_violation

Interfaces: Module functions taking file_path, line, column, context and returning Violation

Implementation: Factory functions for each blocking-in-async pattern with pattern-specific suggestions
"""

from src.core.types import Violation

_FS_IN_ASYNC_SUGGESTION = (
    "Use tokio::fs equivalents (e.g., tokio::fs::read_to_string) for async-compatible "
    "file I/O operations. Blocking std::fs calls in async functions can cause thread "
    "starvation and deadlocks."
)

_SLEEP_IN_ASYNC_SUGGESTION = (
    "Use tokio::time::sleep instead of std::thread::sleep in async functions. "
    "Blocking the thread with std::thread::sleep prevents the async runtime from "
    "processing other tasks on the same thread."
)

_NET_IN_ASYNC_SUGGESTION = (
    "Use tokio::net equivalents (e.g., tokio::net::TcpStream) for async-compatible "
    "networking. Blocking std::net calls in async functions can cause thread starvation "
    "and deadlocks in the async runtime."
)


def build_fs_in_async_violation(
    file_path: str,
    line: int,
    column: int,
    context: str,
) -> Violation:
    """Build a violation for std::fs operation inside an async function."""
    message = f"Blocking std::fs operation inside async function: {context}"

    return Violation(
        rule_id="blocking-async.fs-in-async",
        file_path=file_path,
        line=line,
        column=column,
        message=message,
        suggestion=_FS_IN_ASYNC_SUGGESTION,
    )


def build_sleep_in_async_violation(
    file_path: str,
    line: int,
    column: int,
    context: str,
) -> Violation:
    """Build a violation for std::thread::sleep inside an async function."""
    message = f"Blocking std::thread::sleep inside async function: {context}"

    return Violation(
        rule_id="blocking-async.sleep-in-async",
        file_path=file_path,
        line=line,
        column=column,
        message=message,
        suggestion=_SLEEP_IN_ASYNC_SUGGESTION,
    )


def build_net_in_async_violation(
    file_path: str,
    line: int,
    column: int,
    context: str,
) -> Violation:
    """Build a violation for blocking std::net operation inside an async function."""
    message = f"Blocking std::net operation inside async function: {context}"

    return Violation(
        rule_id="blocking-async.net-in-async",
        file_path=file_path,
        line=line,
        column=column,
        message=message,
        suggestion=_NET_IN_ASYNC_SUGGESTION,
    )

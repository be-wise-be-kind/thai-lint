"""
Purpose: Shared pytest fixtures for blocking-in-async linter tests

Scope: Test configuration, mock contexts, and sample Rust code constants for blocking-in-async detection

Overview: Provides reusable fixtures and sample Rust code for testing the blocking-in-async detector.
    Includes factory function for creating mock lint contexts, configuration fixtures with
    various toggle combinations, and comprehensive Rust code constants covering fs-in-async,
    sleep-in-async, net-in-async, test-aware detection, and edge cases. Designed to mirror
    the clone_abuse conftest pattern for consistency.

Dependencies: pytest, unittest.mock, src.analyzers.rust_base, src.linters.blocking_async.config

Exports: create_mock_context factory, config fixtures, sample Rust code constants

Interfaces: create_mock_context(code, filename, language, metadata) -> Mock

Implementation: Pytest fixtures with factory pattern for mock contexts, skip marker for missing tree-sitter
"""

from pathlib import Path
from typing import Any
from unittest.mock import Mock

import pytest

from src.analyzers.rust_base import TREE_SITTER_RUST_AVAILABLE
from src.linters.blocking_async.config import BlockingAsyncConfig

pytestmark = pytest.mark.skipif(
    not TREE_SITTER_RUST_AVAILABLE, reason="tree-sitter-rust not installed"
)


def create_mock_context(
    code: str,
    filename: str = "main.rs",
    language: str = "rust",
    metadata: dict[str, Any] | None = None,
) -> Mock:
    """Create a mock BaseLintContext for testing.

    Args:
        code: Rust source code content
        filename: File path for the mock context
        language: Language identifier
        metadata: Optional metadata dictionary

    Returns:
        Mock object mimicking BaseLintContext
    """
    context = Mock()
    context.file_content = code
    context.file_path = Path(filename)
    context.language = language
    context.metadata = metadata or {}
    return context


@pytest.fixture
def default_config() -> BlockingAsyncConfig:
    """Default blocking-in-async configuration."""
    return BlockingAsyncConfig()


@pytest.fixture
def strict_config() -> BlockingAsyncConfig:
    """Strict configuration that flags blocking calls in tests."""
    return BlockingAsyncConfig(
        allow_in_tests=False,
    )


@pytest.fixture
def fs_only_config() -> BlockingAsyncConfig:
    """Configuration that only detects fs-in-async."""
    return BlockingAsyncConfig(
        detect_fs_in_async=True,
        detect_sleep_in_async=False,
        detect_net_in_async=False,
    )


@pytest.fixture
def sleep_only_config() -> BlockingAsyncConfig:
    """Configuration that only detects sleep-in-async."""
    return BlockingAsyncConfig(
        detect_fs_in_async=False,
        detect_sleep_in_async=True,
        detect_net_in_async=False,
    )


@pytest.fixture
def mock_context():
    """Factory fixture for creating mock contexts."""

    def _create(code: str, filename: str = "main.rs") -> Mock:
        return create_mock_context(code, filename)

    return _create


# =============================================================================
# Sample Rust Code Constants
# =============================================================================

# Should flag - std::fs in async fn
FS_READ_IN_ASYNC = """
async fn read_file() {
    let content = std::fs::read_to_string("file.txt").unwrap();
}
"""

# Should flag - std::thread::sleep in async fn
SLEEP_IN_ASYNC = """
async fn slow_function() {
    std::thread::sleep(std::time::Duration::from_secs(1));
}
"""

# Should flag - std::net in async fn
NET_IN_ASYNC = """
async fn connect() {
    let stream = std::net::TcpStream::connect("127.0.0.1:8080").unwrap();
}
"""

# Should NOT flag - sync function
FS_READ_IN_SYNC = """
fn read_file() {
    let content = std::fs::read_to_string("file.txt").unwrap();
}
"""

# Should NOT flag - async equivalents
TOKIO_FS_IN_ASYNC = """
async fn read_file() {
    let content = tokio::fs::read_to_string("file.txt").await.unwrap();
}
"""

# Should NOT flag - in test
FS_IN_ASYNC_TEST = """
#[test]
async fn test_read() {
    let content = std::fs::read_to_string("test.txt").unwrap();
}
"""

# Should flag - short path (fs::read_to_string)
SHORT_PATH_FS_IN_ASYNC = """
use std::fs;

async fn read_file() {
    let content = fs::read_to_string("file.txt").unwrap();
}
"""

# Should flag - multiple blocking calls
MULTIPLE_BLOCKING_IN_ASYNC = """
async fn do_stuff() {
    let content = std::fs::read_to_string("file.txt").unwrap();
    std::thread::sleep(std::time::Duration::from_secs(1));
}
"""

# Edge case - empty async function
EMPTY_ASYNC = """
async fn noop() {}
"""

# Edge case - nested async block
NESTED_ASYNC = """
fn outer() {
    let handle = tokio::spawn(async {
        std::fs::read_to_string("file.txt").unwrap();
    });
}
"""

# Should flag - std::fs::write in async fn
FS_WRITE_IN_ASYNC = """
async fn write_file() {
    std::fs::write("output.txt", "data").unwrap();
}
"""

# Should flag - short path thread::sleep
SHORT_PATH_SLEEP_IN_ASYNC = """
use std::thread;

async fn slow_function() {
    thread::sleep(std::time::Duration::from_secs(1));
}
"""

# Should NOT flag - tokio::time::sleep
TOKIO_SLEEP_IN_ASYNC = """
async fn wait() {
    tokio::time::sleep(std::time::Duration::from_secs(1)).await;
}
"""

# cfg(test) module with blocking async
FS_IN_CFG_TEST_ASYNC = """
#[cfg(test)]
mod tests {
    async fn test_helper() {
        let content = std::fs::read_to_string("test.txt").unwrap();
    }
}
"""

# No blocking calls at all
NO_BLOCKING_CALLS = """
async fn process(data: &str) {
    let result = data.to_uppercase();
    println!("{}", result);
}
"""

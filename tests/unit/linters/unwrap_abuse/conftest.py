"""
Purpose: Shared pytest fixtures for unwrap abuse linter tests

Scope: Fixtures for mock contexts, sample Rust code, and configurations

Overview: Provides shared fixtures and helper functions for unwrap abuse linter testing.
    Includes mock context creation, configuration fixtures, and sample Rust code constants
    for testing unwrap/expect detection. Supports TDD approach for all detection scenarios
    including test-aware filtering and path-based ignoring.

Dependencies: pytest, pathlib, unittest.mock

Exports: Fixture functions and test data constants

Interfaces: Factory functions for test setup

Implementation: pytest fixtures with factory pattern for flexible test setup
"""

from pathlib import Path
from typing import Any
from unittest.mock import Mock

import pytest

from src.analyzers.rust_base import TREE_SITTER_RUST_AVAILABLE
from src.linters.unwrap_abuse.config import UnwrapAbuseConfig

# Skip all tests in this directory if tree-sitter-rust is not available
pytestmark = pytest.mark.skipif(
    not TREE_SITTER_RUST_AVAILABLE, reason="tree-sitter-rust not installed"
)


def create_mock_context(
    code: str,
    filename: str = "main.rs",
    language: str = "rust",
    metadata: dict[str, Any] | None = None,
) -> Mock:
    """Create mock lint context for testing.

    Args:
        code: Rust source code content
        filename: File name for the context
        language: Language identifier
        metadata: Optional metadata dictionary

    Returns:
        Mock context with required properties
    """
    context = Mock()
    context.file_content = code
    context.file_path = Path(filename)
    context.language = language
    context.metadata = metadata or {}
    return context


@pytest.fixture
def default_config() -> UnwrapAbuseConfig:
    """Create default unwrap abuse configuration for testing."""
    return UnwrapAbuseConfig()


@pytest.fixture
def strict_config() -> UnwrapAbuseConfig:
    """Create strict config that flags everything including tests and expect."""
    return UnwrapAbuseConfig(
        allow_in_tests=False,
        allow_expect=False,
    )


@pytest.fixture
def expect_allowed_config() -> UnwrapAbuseConfig:
    """Create config that allows .expect() but flags .unwrap()."""
    return UnwrapAbuseConfig(
        allow_expect=True,
    )


@pytest.fixture
def mock_context():
    """Factory for creating mock lint contexts."""

    def _create(code: str, filename: str = "main.rs") -> Mock:
        return create_mock_context(code, filename)

    return _create


# =============================================================================
# Sample Rust Code Constants
# =============================================================================

# Code with .unwrap() calls (should flag)
UNWRAP_SIMPLE = """
fn main() {
    let x = some_function().unwrap();
}
"""

UNWRAP_RESULT = """
fn read_file() -> String {
    let content = std::fs::read_to_string("file.txt").unwrap();
    content
}
"""

UNWRAP_OPTION = """
fn get_first(items: &[i32]) -> i32 {
    *items.first().unwrap()
}
"""

# Code with .expect() calls (should flag unless allow_expect=True)
EXPECT_SIMPLE = """
fn main() {
    let x = some_function().expect("should not fail");
}
"""

EXPECT_WITH_MESSAGE = """
fn connect() -> Connection {
    let conn = Database::connect("url").expect("database connection failed");
    conn
}
"""

# Code with both .unwrap() and .expect()
MIXED_CALLS = """
fn process() {
    let x = foo().unwrap();
    let y = bar().expect("bar failed");
    let z = baz().unwrap();
}
"""

# Code in test context (should NOT flag with default config)
UNWRAP_IN_TEST = """
#[test]
fn test_something() {
    let x = foo().unwrap();
    let y = bar().expect("test failed");
}
"""

UNWRAP_IN_CFG_TEST = """
#[cfg(test)]
mod tests {
    fn test_helper() {
        let x = foo().unwrap();
    }
}
"""

# Clean code (should NOT flag)
PROPER_ERROR_HANDLING = """
fn read_file() -> Result<String, std::io::Error> {
    let content = std::fs::read_to_string("file.txt")?;
    Ok(content)
}
"""

UNWRAP_OR_DEFAULT = """
fn get_value(map: &HashMap<String, String>, key: &str) -> String {
    map.get(key).unwrap_or_default().to_string()
}
"""

UNWRAP_OR_FALLBACK = """
fn get_name(user: Option<&User>) -> &str {
    user.map(|u| u.name.as_str()).unwrap_or("anonymous")
}
"""

MATCH_PATTERN = """
fn process(result: Result<i32, Error>) -> i32 {
    match result {
        Ok(val) => val,
        Err(_) => 0,
    }
}
"""

# Empty file
EMPTY_FILE = ""

"""
Purpose: Shared pytest fixtures for clone abuse linter tests

Scope: Test configuration, mock contexts, and sample Rust code constants for clone abuse detection

Overview: Provides reusable fixtures and sample Rust code for testing the clone abuse detector.
    Includes factory function for creating mock lint contexts, configuration fixtures with
    various toggle combinations, and comprehensive Rust code constants covering clone-in-loop,
    clone-chain, unnecessary-clone, test-aware detection, and edge cases. Designed to mirror
    the unwrap_abuse conftest pattern for consistency.

Dependencies: pytest, unittest.mock, src.analyzers.rust_base, src.linters.clone_abuse.config

Exports: create_mock_context factory, config fixtures, sample Rust code constants

Interfaces: create_mock_context(code, filename, language, metadata) -> Mock

Implementation: Pytest fixtures with factory pattern for mock contexts, skip marker for missing tree-sitter
"""

from pathlib import Path
from typing import Any
from unittest.mock import Mock

import pytest

from src.analyzers.rust_base import TREE_SITTER_RUST_AVAILABLE
from src.linters.clone_abuse.config import CloneAbuseConfig

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
def default_config() -> CloneAbuseConfig:
    """Default clone abuse configuration."""
    return CloneAbuseConfig()


@pytest.fixture
def strict_config() -> CloneAbuseConfig:
    """Strict configuration that flags clones in tests."""
    return CloneAbuseConfig(
        allow_in_tests=False,
    )


@pytest.fixture
def loop_only_config() -> CloneAbuseConfig:
    """Configuration that only detects clone-in-loop."""
    return CloneAbuseConfig(
        detect_clone_in_loop=True,
        detect_clone_chain=False,
        detect_unnecessary_clone=False,
    )


@pytest.fixture
def chain_only_config() -> CloneAbuseConfig:
    """Configuration that only detects clone-chain."""
    return CloneAbuseConfig(
        detect_clone_in_loop=False,
        detect_clone_chain=True,
        detect_unnecessary_clone=False,
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

CLONE_IN_FOR_LOOP = """
fn process(items: &[String]) {
    for item in items {
        let copy = item.clone();
        do_something(copy);
    }
}
"""

CLONE_IN_WHILE_LOOP = """
fn process(data: &String) {
    let mut count = 0;
    while count < 10 {
        let copy = data.clone();
        use_data(copy);
        count += 1;
    }
}
"""

CLONE_IN_LOOP = """
fn process(data: &String) {
    loop {
        let copy = data.clone();
        if should_stop(copy) {
            break;
        }
    }
}
"""

CLONE_CHAIN = """
fn process(data: &String) {
    let redundant = data.clone().clone();
    use_data(redundant);
}
"""

CLONE_BEFORE_MOVE = """
fn process(data: String) {
    let copy = data.clone();
    consume(copy);
}
"""

CLONE_IN_TEST = """
#[test]
fn test_something() {
    let data = String::from("test");
    let copy = data.clone();
    assert_eq!(data, copy);
}
"""

NECESSARY_CLONE = """
fn process(data: &String) {
    let copy = data.clone();
    use_data(copy);
    println!("{}", data);
}
"""

NO_CLONE = """
fn process(data: &str) {
    let borrowed = data;
    println!("{}", borrowed);
}
"""

EMPTY_FILE = ""

CLONE_FIELD_ACCESS = """
fn process(container: &Container) {
    let copy = container.data.clone();
    use_data(copy);
}
"""

MULTIPLE_PATTERNS = """
fn process(items: &[String], data: &String) {
    for item in items {
        let copy = item.clone();
        do_something(copy);
    }
    let redundant = data.clone().clone();
    use_data(redundant);
}
"""

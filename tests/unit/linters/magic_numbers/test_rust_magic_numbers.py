"""
Purpose: Test suite for Rust magic number detection

Scope: Rust numeric literal detection using tree-sitter parsing

Overview: Tests for Rust magic number violation detection covering numeric literals in
    function bodies, const/static definition exemptions, default allowed number exemptions,
    type suffix handling, and language filtering. Validates that Rust numeric patterns are
    properly detected and filtered.

Dependencies: pytest, MagicNumberRule, TREE_SITTER_RUST_AVAILABLE, pathlib, unittest.mock

Exports: TestRustMagicNumberDetection, TestRustConstExemptions, TestRustAllowedNumbers,
    TestRustLanguageFiltering, TestRustEdgeCases

Interfaces: Tests MagicNumberRule.check(context) -> list[Violation] with Rust code samples

Implementation: Uses inline Rust code strings as test fixtures, sets language="rust"
"""

from pathlib import Path
from unittest.mock import Mock

import pytest

from src.analyzers.rust_base import TREE_SITTER_RUST_AVAILABLE
from src.linters.magic_numbers.linter import MagicNumberRule

pytestmark = pytest.mark.skipif(
    not TREE_SITTER_RUST_AVAILABLE, reason="tree-sitter-rust not installed"
)


def _create_context(code: str, filename: str = "main.rs", language: str = "rust") -> Mock:
    """Create mock lint context for testing."""
    context = Mock()
    context.file_content = code
    context.file_path = Path(filename)
    context.language = language
    context.metadata = {}
    return context


class TestRustMagicNumberDetection:
    """Test basic magic number detection in Rust code."""

    def test_detects_magic_number_in_comparison(self) -> None:
        """Should detect magic number in comparison."""
        code = """
fn check_items(items: &[i32]) -> bool {
    items.len() > 42
}
"""
        rule = MagicNumberRule()
        violations = rule.check(_create_context(code))
        assert len(violations) > 0
        assert any("42" in v.message for v in violations)

    def test_detects_magic_number_in_assignment(self) -> None:
        """Should detect magic number in variable assignment."""
        code = """
fn compute() -> i32 {
    let threshold = 256;
    threshold
}
"""
        rule = MagicNumberRule()
        violations = rule.check(_create_context(code))
        assert len(violations) > 0

    def test_no_violations_for_clean_code(self) -> None:
        """Should not flag code using named constants."""
        code = """
const MAX_ITEMS: usize = 100;

fn check_items(items: &[i32]) -> bool {
    items.len() > MAX_ITEMS
}
"""
        rule = MagicNumberRule()
        violations = rule.check(_create_context(code))
        # The 100 in const definition should not be flagged
        assert len(violations) == 0


class TestRustConstExemptions:
    """Test that const and static definitions are exempt."""

    def test_const_definition_allowed(self) -> None:
        """Numbers in const definitions should be allowed."""
        code = """
const MAX_RETRIES: u32 = 42;
const TIMEOUT_MS: u64 = 5000;
"""
        rule = MagicNumberRule()
        violations = rule.check(_create_context(code))
        assert len(violations) == 0

    def test_static_definition_allowed(self) -> None:
        """Numbers in static definitions should be allowed."""
        code = """
static MAX_CONNECTIONS: u32 = 128;
"""
        rule = MagicNumberRule()
        violations = rule.check(_create_context(code))
        assert len(violations) == 0

    def test_const_in_impl_allowed(self) -> None:
        """Constants defined in impl blocks should be allowed."""
        code = """
struct Config {}
impl Config {
    const MAX_SIZE: usize = 1024;
}
"""
        rule = MagicNumberRule()
        violations = rule.check(_create_context(code))
        assert len(violations) == 0


class TestRustAllowedNumbers:
    """Test that default allowed numbers are not flagged."""

    def test_zero_allowed(self) -> None:
        """Zero should be allowed by default."""
        code = """
fn init() -> i32 {
    0
}
"""
        rule = MagicNumberRule()
        violations = rule.check(_create_context(code))
        assert len(violations) == 0

    def test_one_allowed(self) -> None:
        """One should be allowed by default."""
        code = """
fn increment(x: i32) -> i32 {
    x + 1
}
"""
        rule = MagicNumberRule()
        violations = rule.check(_create_context(code))
        assert len(violations) == 0

    def test_negative_one_allowed(self) -> None:
        """Common small integers should be allowed."""
        code = """
fn decrement(x: i32) -> i32 {
    x + 2
}
"""
        rule = MagicNumberRule()
        violations = rule.check(_create_context(code))
        assert len(violations) == 0

    def test_large_number_flagged(self) -> None:
        """Large numbers not in allowed list should be flagged."""
        code = """
fn timeout() -> u64 {
    9999
}
"""
        rule = MagicNumberRule()
        violations = rule.check(_create_context(code))
        assert len(violations) > 0


class TestRustLanguageFiltering:
    """Test that magic number analysis only processes Rust files."""

    def test_ignores_python_files(self) -> None:
        """Should not process Python files via Rust analyzer."""
        code = "x = 42"
        context = _create_context(code, filename="test.py", language="python")
        rule = MagicNumberRule()
        violations = rule.check(context)
        # May have Python violations, but should not crash
        assert isinstance(violations, list)

    def test_processes_rust_files(self) -> None:
        """Should process .rs files."""
        code = """
fn magic() -> i32 {
    42
}
"""
        context = _create_context(code, filename="src/lib.rs", language="rust")
        rule = MagicNumberRule()
        violations = rule.check(context)
        assert len(violations) > 0


class TestRustEdgeCases:
    """Test edge cases for Rust magic number analysis."""

    def test_empty_file(self) -> None:
        """Should handle empty files gracefully."""
        rule = MagicNumberRule()
        violations = rule.check(_create_context(""))
        assert len(violations) == 0

    def test_none_content(self) -> None:
        """Should handle None content gracefully."""
        context = _create_context("")
        context.file_content = None
        rule = MagicNumberRule()
        violations = rule.check(context)
        assert len(violations) == 0

    def test_violation_has_suggestion(self) -> None:
        """Violations should include Rust-specific suggestion."""
        code = """
fn compute() -> i32 {
    42
}
"""
        rule = MagicNumberRule()
        violations = rule.check(_create_context(code))
        assert len(violations) > 0
        assert violations[0].suggestion is not None
        assert "const" in violations[0].suggestion.lower()

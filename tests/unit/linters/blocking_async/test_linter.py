"""
Purpose: Unit tests for BlockingAsyncRule linter

Scope: Tests for rule properties, detection, test filtering, pattern toggles, language filtering,
    ignored paths, disabled state, and edge cases

Overview: Comprehensive test suite for the BlockingAsyncRule class covering its integration of
    config loading, analyzer delegation, and violation building. Validates that the rule
    correctly detects fs-in-async, sleep-in-async, and net-in-async patterns while
    respecting configuration for test filtering, pattern toggles, ignored paths, and
    language filtering. Follows the clone_abuse test_linter pattern for consistency.

Dependencies: pytest, src.analyzers.rust_base, src.linters.blocking_async

Exports: Test classes for each aspect of BlockingAsyncRule behavior

Interfaces: Standard pytest test classes

Implementation: Direct rule instantiation with mock contexts and config overrides
"""

import pytest

from src.analyzers.rust_base import TREE_SITTER_RUST_AVAILABLE
from src.linters.blocking_async.config import BlockingAsyncConfig
from src.linters.blocking_async.linter import BlockingAsyncRule

from .conftest import create_mock_context

pytestmark = pytest.mark.skipif(
    not TREE_SITTER_RUST_AVAILABLE, reason="tree-sitter-rust not installed"
)


class TestBlockingAsyncRuleProperties:
    """Tests for rule metadata properties."""

    def test_rule_id(self) -> None:
        """Should have correct rule_id."""
        rule = BlockingAsyncRule()
        assert rule.rule_id == "blocking-async"

    def test_rule_name(self) -> None:
        """Should have correct rule_name."""
        rule = BlockingAsyncRule()
        assert rule.rule_name == "Rust Blocking in Async"

    def test_description(self) -> None:
        """Should have a description mentioning blocking and async."""
        rule = BlockingAsyncRule()
        assert "blocking" in rule.description.lower()
        assert "async" in rule.description.lower()


class TestBlockingAsyncRuleDetection:
    """Tests for blocking pattern detection via check()."""

    def test_detects_fs_in_async(self) -> None:
        """Should detect std::fs operation inside an async function."""
        code = """
async fn read_file() {
    let content = std::fs::read_to_string("file.txt").unwrap();
}
"""
        context = create_mock_context(code)
        rule = BlockingAsyncRule()
        violations = rule.check(context)
        fs_violations = [v for v in violations if "fs-in-async" in v.rule_id]
        assert len(fs_violations) >= 1

    def test_detects_sleep_in_async(self) -> None:
        """Should detect std::thread::sleep inside an async function."""
        code = """
async fn slow_function() {
    std::thread::sleep(std::time::Duration::from_secs(1));
}
"""
        context = create_mock_context(code)
        rule = BlockingAsyncRule()
        violations = rule.check(context)
        sleep_violations = [v for v in violations if "sleep-in-async" in v.rule_id]
        assert len(sleep_violations) >= 1

    def test_detects_net_in_async(self) -> None:
        """Should detect blocking std::net operation inside an async function."""
        code = """
async fn connect() {
    let stream = std::net::TcpStream::connect("127.0.0.1:8080").unwrap();
}
"""
        context = create_mock_context(code)
        rule = BlockingAsyncRule()
        violations = rule.check(context)
        net_violations = [v for v in violations if "net-in-async" in v.rule_id]
        assert len(net_violations) >= 1

    def test_no_violations_for_sync_code(self) -> None:
        """Should produce no violations for blocking calls in sync functions."""
        code = """
fn read_file() {
    let content = std::fs::read_to_string("file.txt").unwrap();
}
"""
        context = create_mock_context(code)
        rule = BlockingAsyncRule()
        violations = rule.check(context)
        assert len(violations) == 0

    def test_no_violations_for_tokio_calls(self) -> None:
        """Should produce no violations for async-compatible tokio calls."""
        code = """
async fn read_file() {
    let content = tokio::fs::read_to_string("file.txt").await.unwrap();
}
"""
        context = create_mock_context(code)
        rule = BlockingAsyncRule()
        violations = rule.check(context)
        assert len(violations) == 0

    def test_violation_has_suggestion(self) -> None:
        """Should include a non-empty suggestion in each violation."""
        code = """
async fn read_file() {
    let content = std::fs::read_to_string("file.txt").unwrap();
}
"""
        context = create_mock_context(code)
        rule = BlockingAsyncRule()
        violations = rule.check(context)
        assert len(violations) >= 1
        assert violations[0].suggestion is not None
        assert len(violations[0].suggestion) > 0


class TestBlockingAsyncRuleTestFiltering:
    """Tests for test code filtering behavior."""

    def test_ignores_blocking_in_test_by_default(self) -> None:
        """Should ignore blocking calls in test code by default."""
        code = """
#[test]
async fn test_read() {
    let content = std::fs::read_to_string("test.txt").unwrap();
}
"""
        context = create_mock_context(code)
        rule = BlockingAsyncRule()
        violations = rule.check(context)
        assert len(violations) == 0

    def test_flags_test_code_when_configured(self) -> None:
        """Should flag blocking calls in test code when allow_in_tests is False."""
        code = """
#[test]
async fn test_read() {
    let content = std::fs::read_to_string("test.txt").unwrap();
}
"""
        context = create_mock_context(code)
        config = BlockingAsyncConfig(allow_in_tests=False)
        rule = BlockingAsyncRule(config=config)
        violations = rule.check(context)
        assert len(violations) >= 1


class TestBlockingAsyncRulePatternToggles:
    """Tests for pattern toggle configuration."""

    def test_disabling_fs_detection(self) -> None:
        """Should skip fs-in-async detection when disabled in config."""
        code = """
async fn read_file() {
    let content = std::fs::read_to_string("file.txt").unwrap();
}
"""
        context = create_mock_context(code)
        config = BlockingAsyncConfig(detect_fs_in_async=False)
        rule = BlockingAsyncRule(config=config)
        violations = rule.check(context)
        fs_violations = [v for v in violations if "fs-in-async" in v.rule_id]
        assert len(fs_violations) == 0

    def test_disabling_sleep_detection(self) -> None:
        """Should skip sleep-in-async detection when disabled in config."""
        code = """
async fn slow_function() {
    std::thread::sleep(std::time::Duration::from_secs(1));
}
"""
        context = create_mock_context(code)
        config = BlockingAsyncConfig(detect_sleep_in_async=False)
        rule = BlockingAsyncRule(config=config)
        violations = rule.check(context)
        sleep_violations = [v for v in violations if "sleep-in-async" in v.rule_id]
        assert len(sleep_violations) == 0

    def test_disabling_net_detection(self) -> None:
        """Should skip net-in-async detection when disabled in config."""
        code = """
async fn connect() {
    let stream = std::net::TcpStream::connect("127.0.0.1:8080").unwrap();
}
"""
        context = create_mock_context(code)
        config = BlockingAsyncConfig(detect_net_in_async=False)
        rule = BlockingAsyncRule(config=config)
        violations = rule.check(context)
        net_violations = [v for v in violations if "net-in-async" in v.rule_id]
        assert len(net_violations) == 0


class TestBlockingAsyncRuleLanguageFiltering:
    """Tests for language filtering behavior."""

    def test_ignores_non_rust_files(self) -> None:
        """Should produce no violations for Python files."""
        code = "std::fs::read_to_string  # looks like Rust but is Python"
        context = create_mock_context(code, filename="test.py", language="python")
        rule = BlockingAsyncRule()
        violations = rule.check(context)
        assert len(violations) == 0

    def test_ignores_typescript_files(self) -> None:
        """Should produce no violations for TypeScript files."""
        code = "const x = std.fs.readFileSync();"
        context = create_mock_context(code, filename="test.ts", language="typescript")
        rule = BlockingAsyncRule()
        violations = rule.check(context)
        assert len(violations) == 0


class TestBlockingAsyncRuleIgnoredPaths:
    """Tests for ignored path patterns."""

    def test_ignores_examples_directory(self) -> None:
        """Should ignore blocking calls in the examples directory."""
        code = """
async fn read_file() {
    let content = std::fs::read_to_string("file.txt").unwrap();
}
"""
        context = create_mock_context(code, filename="examples/demo.rs")
        rule = BlockingAsyncRule()
        violations = rule.check(context)
        assert len(violations) == 0

    def test_ignores_benches_directory(self) -> None:
        """Should ignore blocking calls in the benches directory."""
        code = """
async fn read_file() {
    let content = std::fs::read_to_string("file.txt").unwrap();
}
"""
        context = create_mock_context(code, filename="benches/benchmark.rs")
        rule = BlockingAsyncRule()
        violations = rule.check(context)
        assert len(violations) == 0

    def test_does_not_ignore_src_directory(self) -> None:
        """Should detect blocking calls in the src directory."""
        code = """
async fn read_file() {
    let content = std::fs::read_to_string("file.txt").unwrap();
}
"""
        context = create_mock_context(code, filename="src/main.rs")
        rule = BlockingAsyncRule()
        violations = rule.check(context)
        assert len(violations) >= 1


class TestBlockingAsyncRuleDisabled:
    """Tests for disabled rule state."""

    def test_returns_empty_when_disabled(self) -> None:
        """Should return no violations when the rule is disabled."""
        code = """
async fn read_file() {
    let content = std::fs::read_to_string("file.txt").unwrap();
}
"""
        context = create_mock_context(code)
        config = BlockingAsyncConfig(enabled=False)
        rule = BlockingAsyncRule(config=config)
        violations = rule.check(context)
        assert len(violations) == 0


class TestBlockingAsyncRuleEdgeCases:
    """Tests for edge cases."""

    def test_empty_file(self) -> None:
        """Should return no violations for an empty file."""
        context = create_mock_context("")
        rule = BlockingAsyncRule()
        violations = rule.check(context)
        assert len(violations) == 0

    def test_none_content(self) -> None:
        """Should return no violations when file content is None."""
        context = create_mock_context("")
        context.file_content = None
        rule = BlockingAsyncRule()
        violations = rule.check(context)
        assert len(violations) == 0

    def test_non_rust_language(self) -> None:
        """Should return no violations for non-Rust languages."""
        context = create_mock_context("std::fs::read()", language="python")
        rule = BlockingAsyncRule()
        violations = rule.check(context)
        assert len(violations) == 0

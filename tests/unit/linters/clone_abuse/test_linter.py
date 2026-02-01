"""
Purpose: Unit tests for CloneAbuseRule linter

Scope: Tests for rule properties, detection, test filtering, pattern toggles, language filtering,
    ignored paths, disabled state, and edge cases

Overview: Comprehensive test suite for the CloneAbuseRule class covering its integration of
    config loading, analyzer delegation, and violation building. Validates that the rule
    correctly detects clone-in-loop, clone-chain, and unnecessary-clone patterns while
    respecting configuration for test filtering, pattern toggles, ignored paths, and
    language filtering. Follows the unwrap_abuse test_linter pattern for consistency.

Dependencies: pytest, src.analyzers.rust_base, src.linters.clone_abuse

Exports: Test classes for each aspect of CloneAbuseRule behavior

Interfaces: Standard pytest test classes

Implementation: Direct rule instantiation with mock contexts and config overrides
"""

import pytest

from src.analyzers.rust_base import TREE_SITTER_RUST_AVAILABLE
from src.linters.clone_abuse.config import CloneAbuseConfig
from src.linters.clone_abuse.linter import CloneAbuseRule

from .conftest import create_mock_context

pytestmark = pytest.mark.skipif(
    not TREE_SITTER_RUST_AVAILABLE, reason="tree-sitter-rust not installed"
)


class TestCloneAbuseRuleProperties:
    """Tests for rule metadata properties."""

    def test_rule_id(self) -> None:
        """Should have correct rule_id."""
        rule = CloneAbuseRule()
        assert rule.rule_id == "clone-abuse"

    def test_rule_name(self) -> None:
        """Should have correct rule_name."""
        rule = CloneAbuseRule()
        assert rule.rule_name == "Rust Clone Abuse"

    def test_description(self) -> None:
        """Should have a description mentioning clone."""
        rule = CloneAbuseRule()
        assert "clone" in rule.description.lower()


class TestCloneAbuseRuleDetection:
    """Tests for clone pattern detection via check()."""

    def test_detects_clone_in_loop(self) -> None:
        """Should detect clone called inside a loop."""
        code = """
fn process(items: &[String]) {
    for item in items {
        let copy = item.clone();
        do_something(copy);
    }
}
"""
        context = create_mock_context(code)
        rule = CloneAbuseRule()
        violations = rule.check(context)
        loop_violations = [v for v in violations if "clone-in-loop" in v.rule_id]
        assert len(loop_violations) >= 1

    def test_detects_clone_chain(self) -> None:
        """Should detect chained clone calls."""
        code = """
fn process(data: &String) {
    let redundant = data.clone().clone();
    use_data(redundant);
}
"""
        context = create_mock_context(code)
        rule = CloneAbuseRule()
        violations = rule.check(context)
        chain_violations = [v for v in violations if "clone-chain" in v.rule_id]
        assert len(chain_violations) >= 1

    def test_detects_unnecessary_clone(self) -> None:
        """Should detect unnecessary clone on an owned value."""
        code = """
fn process(data: String) {
    let copy = data.clone();
    consume(copy);
}
"""
        context = create_mock_context(code)
        rule = CloneAbuseRule()
        violations = rule.check(context)
        unnecessary_violations = [v for v in violations if "unnecessary-clone" in v.rule_id]
        assert len(unnecessary_violations) >= 1

    def test_no_violations_for_clean_code(self) -> None:
        """Should produce no violations for code without clone abuse."""
        code = """
fn process(data: &str) {
    let borrowed = data;
    println!("{}", borrowed);
}
"""
        context = create_mock_context(code)
        rule = CloneAbuseRule()
        violations = rule.check(context)
        assert len(violations) == 0

    def test_violation_has_suggestion(self) -> None:
        """Should include a non-empty suggestion in each violation."""
        code = """
fn process(items: &[String]) {
    for item in items {
        let copy = item.clone();
        do_something(copy);
    }
}
"""
        context = create_mock_context(code)
        rule = CloneAbuseRule()
        violations = rule.check(context)
        assert len(violations) >= 1
        assert violations[0].suggestion is not None
        assert len(violations[0].suggestion) > 0


class TestCloneAbuseRuleTestFiltering:
    """Tests for test code filtering behavior."""

    def test_ignores_clone_in_test_by_default(self) -> None:
        """Should ignore clone abuse in test code by default."""
        code = """
#[test]
fn test_something() {
    let data = String::from("test");
    let copy = data.clone();
    assert_eq!(data, copy);
}
"""
        context = create_mock_context(code)
        rule = CloneAbuseRule()
        violations = rule.check(context)
        assert len(violations) == 0

    def test_flags_test_code_when_configured(self) -> None:
        """Should flag clone abuse in test code when allow_in_tests is False."""
        code = """
#[test]
fn test_something() {
    for item in items {
        let copy = item.clone();
    }
}
"""
        context = create_mock_context(code)
        config = CloneAbuseConfig(allow_in_tests=False)
        rule = CloneAbuseRule(config=config)
        violations = rule.check(context)
        assert len(violations) >= 1


class TestCloneAbuseRulePatternToggles:
    """Tests for pattern toggle configuration."""

    def test_disabling_loop_detection(self) -> None:
        """Should skip clone-in-loop detection when disabled in config."""
        code = """
fn process(items: &[String]) {
    for item in items {
        let copy = item.clone();
        do_something(copy);
    }
}
"""
        context = create_mock_context(code)
        config = CloneAbuseConfig(detect_clone_in_loop=False)
        rule = CloneAbuseRule(config=config)
        violations = rule.check(context)
        loop_violations = [v for v in violations if "clone-in-loop" in v.rule_id]
        assert len(loop_violations) == 0

    def test_disabling_chain_detection(self) -> None:
        """Should skip clone-chain detection when disabled in config."""
        code = """
fn process(data: &String) {
    let redundant = data.clone().clone();
    use_data(redundant);
}
"""
        context = create_mock_context(code)
        config = CloneAbuseConfig(detect_clone_chain=False)
        rule = CloneAbuseRule(config=config)
        violations = rule.check(context)
        chain_violations = [v for v in violations if "clone-chain" in v.rule_id]
        assert len(chain_violations) == 0

    def test_disabling_unnecessary_clone_detection(self) -> None:
        """Should skip unnecessary-clone detection when disabled in config."""
        code = """
fn process(data: String) {
    let copy = data.clone();
    consume(copy);
}
"""
        context = create_mock_context(code)
        config = CloneAbuseConfig(detect_unnecessary_clone=False)
        rule = CloneAbuseRule(config=config)
        violations = rule.check(context)
        unnecessary_violations = [v for v in violations if "unnecessary-clone" in v.rule_id]
        assert len(unnecessary_violations) == 0


class TestCloneAbuseRuleLanguageFiltering:
    """Tests for language filtering behavior."""

    def test_ignores_non_rust_files(self) -> None:
        """Should produce no violations for Python files."""
        code = "data.clone()  # looks like Rust but is Python"
        context = create_mock_context(code, filename="test.py", language="python")
        rule = CloneAbuseRule()
        violations = rule.check(context)
        assert len(violations) == 0

    def test_ignores_typescript_files(self) -> None:
        """Should produce no violations for TypeScript files."""
        code = "const x = something.clone();"
        context = create_mock_context(code, filename="test.ts", language="typescript")
        rule = CloneAbuseRule()
        violations = rule.check(context)
        assert len(violations) == 0


class TestCloneAbuseRuleIgnoredPaths:
    """Tests for ignored path patterns."""

    def test_ignores_examples_directory(self) -> None:
        """Should ignore clone abuse in the examples directory."""
        code = """
fn process(items: &[String]) {
    for item in items {
        let copy = item.clone();
    }
}
"""
        context = create_mock_context(code, filename="examples/demo.rs")
        rule = CloneAbuseRule()
        violations = rule.check(context)
        assert len(violations) == 0

    def test_ignores_benches_directory(self) -> None:
        """Should ignore clone abuse in the benches directory."""
        code = """
fn process(items: &[String]) {
    for item in items {
        let copy = item.clone();
    }
}
"""
        context = create_mock_context(code, filename="benches/benchmark.rs")
        rule = CloneAbuseRule()
        violations = rule.check(context)
        assert len(violations) == 0

    def test_does_not_ignore_src_directory(self) -> None:
        """Should detect clone abuse in the src directory."""
        code = """
fn process(items: &[String]) {
    for item in items {
        let copy = item.clone();
        do_something(copy);
    }
}
"""
        context = create_mock_context(code, filename="src/main.rs")
        rule = CloneAbuseRule()
        violations = rule.check(context)
        assert len(violations) >= 1


class TestCloneAbuseRuleDisabled:
    """Tests for disabled rule state."""

    def test_returns_empty_when_disabled(self) -> None:
        """Should return no violations when the rule is disabled."""
        code = """
fn process(items: &[String]) {
    for item in items {
        let copy = item.clone();
    }
}
"""
        context = create_mock_context(code)
        config = CloneAbuseConfig(enabled=False)
        rule = CloneAbuseRule(config=config)
        violations = rule.check(context)
        assert len(violations) == 0


class TestCloneAbuseRuleEdgeCases:
    """Tests for edge cases."""

    def test_empty_file(self) -> None:
        """Should return no violations for an empty file."""
        context = create_mock_context("")
        rule = CloneAbuseRule()
        violations = rule.check(context)
        assert len(violations) == 0

    def test_none_content(self) -> None:
        """Should return no violations when file content is None."""
        context = create_mock_context("")
        context.file_content = None
        rule = CloneAbuseRule()
        violations = rule.check(context)
        assert len(violations) == 0

    def test_non_rust_language(self) -> None:
        """Should return no violations for non-Rust languages."""
        context = create_mock_context("data.clone()", language="python")
        rule = CloneAbuseRule()
        violations = rule.check(context)
        assert len(violations) == 0

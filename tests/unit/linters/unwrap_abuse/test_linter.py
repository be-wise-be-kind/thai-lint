"""
Purpose: Unit tests for UnwrapAbuseRule linter

Scope: Tests for the main linter rule including properties, detection, config, and filtering

Overview: Comprehensive test suite for UnwrapAbuseRule. Tests cover rule properties
    (rule_id, rule_name, description), detection of unwrap/expect calls in Rust code,
    test-aware filtering, configuration-based behavior (allow_expect, allow_in_tests),
    ignored path handling, language filtering (only processes Rust files), and edge cases.

Dependencies: pytest, UnwrapAbuseRule, UnwrapAbuseConfig, TREE_SITTER_RUST_AVAILABLE

Exports: Test classes for linter rule behavior

Interfaces: Standard pytest test methods

Implementation: Rule testing via check() method with mock contexts
"""

import pytest

from src.analyzers.rust_base import TREE_SITTER_RUST_AVAILABLE
from src.linters.unwrap_abuse.config import UnwrapAbuseConfig
from src.linters.unwrap_abuse.linter import UnwrapAbuseRule

from .conftest import create_mock_context

pytestmark = pytest.mark.skipif(
    not TREE_SITTER_RUST_AVAILABLE, reason="tree-sitter-rust not installed"
)


class TestUnwrapAbuseRuleProperties:
    """Tests for rule metadata properties."""

    def test_rule_id(self) -> None:
        """Should have correct rule ID."""
        rule = UnwrapAbuseRule()
        assert rule.rule_id == "unwrap-abuse"

    def test_rule_name(self) -> None:
        """Should have human-readable name."""
        rule = UnwrapAbuseRule()
        assert rule.rule_name == "Rust Unwrap Abuse"

    def test_description(self) -> None:
        """Should have descriptive description."""
        rule = UnwrapAbuseRule()
        assert "unwrap" in rule.description.lower()
        assert "expect" in rule.description.lower()


class TestUnwrapAbuseRuleDetection:
    """Tests for violation detection."""

    def test_detects_unwrap_in_non_test_code(self) -> None:
        """Should detect .unwrap() in non-test Rust code."""
        code = """
fn main() {
    let x = foo().unwrap();
}
"""
        context = create_mock_context(code)
        rule = UnwrapAbuseRule()
        violations = rule.check(context)

        assert len(violations) == 1
        assert violations[0].rule_id == "unwrap-abuse.unwrap-call"

    def test_detects_expect_in_non_test_code(self) -> None:
        """Should detect .expect() in non-test Rust code."""
        code = """
fn main() {
    let x = foo().expect("should work");
}
"""
        context = create_mock_context(code)
        rule = UnwrapAbuseRule()
        violations = rule.check(context)

        assert len(violations) == 1
        assert violations[0].rule_id == "unwrap-abuse.expect-call"

    def test_detects_multiple_violations(self) -> None:
        """Should detect multiple unwrap/expect calls."""
        code = """
fn process() {
    let x = foo().unwrap();
    let y = bar().expect("bar failed");
    let z = baz().unwrap();
}
"""
        context = create_mock_context(code)
        rule = UnwrapAbuseRule()
        violations = rule.check(context)

        assert len(violations) == 3

    def test_no_violations_for_clean_code(self) -> None:
        """Should not flag code with proper error handling."""
        code = """
fn process() -> Result<(), Box<dyn std::error::Error>> {
    let x = foo()?;
    let y = bar().unwrap_or_default();
    Ok(())
}
"""
        context = create_mock_context(code)
        rule = UnwrapAbuseRule()
        violations = rule.check(context)

        assert len(violations) == 0

    def test_violation_has_suggestion(self) -> None:
        """Should include suggestion in violations."""
        code = "fn main() { foo().unwrap(); }"
        context = create_mock_context(code)
        rule = UnwrapAbuseRule()
        violations = rule.check(context)

        assert len(violations) == 1
        assert violations[0].suggestion is not None
        assert len(violations[0].suggestion) > 0


class TestUnwrapAbuseRuleTestFiltering:
    """Tests for test-aware filtering."""

    def test_ignores_unwrap_in_test_by_default(self) -> None:
        """Should ignore .unwrap() in #[test] functions by default."""
        code = """
#[test]
fn test_something() {
    let x = foo().unwrap();
}
"""
        context = create_mock_context(code)
        rule = UnwrapAbuseRule()
        violations = rule.check(context)

        assert len(violations) == 0

    def test_ignores_unwrap_in_cfg_test_by_default(self) -> None:
        """Should ignore .unwrap() in #[cfg(test)] modules by default."""
        code = """
#[cfg(test)]
mod tests {
    fn test_helper() {
        let x = foo().unwrap();
    }
}
"""
        context = create_mock_context(code)
        rule = UnwrapAbuseRule()
        violations = rule.check(context)

        assert len(violations) == 0

    def test_flags_test_code_when_configured(self) -> None:
        """Should flag test code when allow_in_tests=False."""
        code = """
#[test]
fn test_something() {
    let x = foo().unwrap();
}
"""
        context = create_mock_context(code)
        config = UnwrapAbuseConfig(allow_in_tests=False)
        rule = UnwrapAbuseRule(config=config)
        violations = rule.check(context)

        assert len(violations) == 1


class TestUnwrapAbuseRuleExpectConfig:
    """Tests for .expect() configuration."""

    def test_allows_expect_when_configured(self) -> None:
        """Should allow .expect() when allow_expect=True."""
        code = """
fn main() {
    let x = foo().expect("should work");
}
"""
        context = create_mock_context(code)
        config = UnwrapAbuseConfig(allow_expect=True)
        rule = UnwrapAbuseRule(config=config)
        violations = rule.check(context)

        assert len(violations) == 0

    def test_still_flags_unwrap_when_expect_allowed(self) -> None:
        """Should still flag .unwrap() even when expect is allowed."""
        code = """
fn main() {
    let x = foo().unwrap();
    let y = bar().expect("msg");
}
"""
        context = create_mock_context(code)
        config = UnwrapAbuseConfig(allow_expect=True)
        rule = UnwrapAbuseRule(config=config)
        violations = rule.check(context)

        assert len(violations) == 1
        assert violations[0].rule_id == "unwrap-abuse.unwrap-call"


class TestUnwrapAbuseRuleLanguageFiltering:
    """Tests for language-based filtering."""

    def test_ignores_non_rust_files(self) -> None:
        """Should not process non-Rust files."""
        code = "result.unwrap()  # looks like Rust but is Python"
        context = create_mock_context(code, filename="test.py", language="python")
        rule = UnwrapAbuseRule()
        violations = rule.check(context)

        assert len(violations) == 0

    def test_ignores_typescript_files(self) -> None:
        """Should not process TypeScript files."""
        code = "const x = something.unwrap();"
        context = create_mock_context(code, filename="test.ts", language="typescript")
        rule = UnwrapAbuseRule()
        violations = rule.check(context)

        assert len(violations) == 0


class TestUnwrapAbuseRuleIgnoredPaths:
    """Tests for path-based ignoring."""

    def test_ignores_examples_directory(self) -> None:
        """Should ignore files in examples/ directory."""
        code = "fn main() { foo().unwrap(); }"
        context = create_mock_context(code, filename="examples/demo.rs")
        rule = UnwrapAbuseRule()
        violations = rule.check(context)

        assert len(violations) == 0

    def test_ignores_benches_directory(self) -> None:
        """Should ignore files in benches/ directory."""
        code = "fn main() { foo().unwrap(); }"
        context = create_mock_context(code, filename="benches/benchmark.rs")
        rule = UnwrapAbuseRule()
        violations = rule.check(context)

        assert len(violations) == 0

    def test_does_not_ignore_src_directory(self) -> None:
        """Should process files in src/ directory."""
        code = "fn main() { foo().unwrap(); }"
        context = create_mock_context(code, filename="src/main.rs")
        rule = UnwrapAbuseRule()
        violations = rule.check(context)

        assert len(violations) == 1


class TestUnwrapAbuseRuleDisabled:
    """Tests for disabled configuration."""

    def test_returns_empty_when_disabled(self) -> None:
        """Should return no violations when disabled."""
        code = "fn main() { foo().unwrap(); }"
        context = create_mock_context(code)
        config = UnwrapAbuseConfig(enabled=False)
        rule = UnwrapAbuseRule(config=config)
        violations = rule.check(context)

        assert len(violations) == 0


class TestUnwrapAbuseRuleEdgeCases:
    """Tests for edge cases."""

    def test_empty_file(self) -> None:
        """Should handle empty files gracefully."""
        context = create_mock_context("")
        rule = UnwrapAbuseRule()
        violations = rule.check(context)

        assert len(violations) == 0

    def test_none_content(self) -> None:
        """Should handle None content gracefully."""
        context = create_mock_context("")
        context.file_content = None
        rule = UnwrapAbuseRule()
        violations = rule.check(context)

        assert len(violations) == 0

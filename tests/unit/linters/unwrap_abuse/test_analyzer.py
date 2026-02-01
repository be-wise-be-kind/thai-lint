"""
Purpose: Unit tests for RustUnwrapAnalyzer

Scope: Tests for unwrap/expect call detection using tree-sitter AST analysis

Overview: Comprehensive test suite for RustUnwrapAnalyzer. Tests cover detection of .unwrap()
    and .expect() calls, test-awareness (detecting calls inside #[test] and #[cfg(test)]),
    edge cases like empty files and code without unwrap calls, and context extraction for
    violation messages.

Dependencies: pytest, RustUnwrapAnalyzer, TREE_SITTER_RUST_AVAILABLE

Exports: Test classes for analyzer behavior

Interfaces: Standard pytest test methods

Implementation: Direct analyzer testing with sample Rust code snippets
"""

import pytest

from src.analyzers.rust_base import TREE_SITTER_RUST_AVAILABLE
from src.linters.unwrap_abuse.rust_analyzer import RustUnwrapAnalyzer

pytestmark = pytest.mark.skipif(
    not TREE_SITTER_RUST_AVAILABLE, reason="tree-sitter-rust not installed"
)


class TestRustUnwrapAnalyzerBasicDetection:
    """Tests for basic unwrap/expect detection."""

    def test_detects_unwrap_call(self) -> None:
        """Should detect .unwrap() calls."""
        analyzer = RustUnwrapAnalyzer()
        code = "fn main() { let x = foo().unwrap(); }"
        calls = analyzer.find_unwrap_calls(code)

        assert len(calls) == 1
        assert calls[0].method == "unwrap"

    def test_detects_expect_call(self) -> None:
        """Should detect .expect() calls."""
        analyzer = RustUnwrapAnalyzer()
        code = 'fn main() { let x = foo().expect("msg"); }'
        calls = analyzer.find_unwrap_calls(code)

        assert len(calls) == 1
        assert calls[0].method == "expect"

    def test_detects_multiple_unwrap_calls(self) -> None:
        """Should detect multiple unwrap calls in one function."""
        analyzer = RustUnwrapAnalyzer()
        code = """
fn main() {
    let x = foo().unwrap();
    let y = bar().unwrap();
    let z = baz().unwrap();
}
"""
        calls = analyzer.find_unwrap_calls(code)
        assert len(calls) == 3
        assert all(c.method == "unwrap" for c in calls)

    def test_detects_mixed_unwrap_and_expect(self) -> None:
        """Should detect both unwrap and expect calls."""
        analyzer = RustUnwrapAnalyzer()
        code = """
fn process() {
    let x = foo().unwrap();
    let y = bar().expect("bar failed");
}
"""
        calls = analyzer.find_unwrap_calls(code)
        assert len(calls) == 2
        methods = {c.method for c in calls}
        assert methods == {"unwrap", "expect"}

    def test_no_calls_in_clean_code(self) -> None:
        """Should return empty list for code without unwrap/expect."""
        analyzer = RustUnwrapAnalyzer()
        code = """
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let x = foo()?;
    Ok(())
}
"""
        calls = analyzer.find_unwrap_calls(code)
        assert len(calls) == 0

    def test_ignores_unwrap_or(self) -> None:
        """Should not flag .unwrap_or() calls."""
        analyzer = RustUnwrapAnalyzer()
        code = 'fn main() { let x = foo().unwrap_or("default"); }'
        calls = analyzer.find_unwrap_calls(code)
        assert len(calls) == 0

    def test_ignores_unwrap_or_default(self) -> None:
        """Should not flag .unwrap_or_default() calls."""
        analyzer = RustUnwrapAnalyzer()
        code = "fn main() { let x = foo().unwrap_or_default(); }"
        calls = analyzer.find_unwrap_calls(code)
        assert len(calls) == 0

    def test_ignores_unwrap_or_else(self) -> None:
        """Should not flag .unwrap_or_else() calls."""
        analyzer = RustUnwrapAnalyzer()
        code = "fn main() { let x = foo().unwrap_or_else(|| default_val()); }"
        calls = analyzer.find_unwrap_calls(code)
        assert len(calls) == 0


class TestRustUnwrapAnalyzerLineInfo:
    """Tests for line and column information accuracy."""

    def test_correct_line_number(self) -> None:
        """Should report correct 1-indexed line numbers."""
        analyzer = RustUnwrapAnalyzer()
        code = """fn main() {
    let a = 1;
    let b = foo().unwrap();
    let c = 2;
}
"""
        calls = analyzer.find_unwrap_calls(code)
        assert len(calls) == 1
        assert calls[0].line == 3

    def test_correct_column_number(self) -> None:
        """Should report correct 0-indexed column numbers."""
        analyzer = RustUnwrapAnalyzer()
        code = "fn main() { let x = foo().unwrap(); }"
        calls = analyzer.find_unwrap_calls(code)
        assert len(calls) == 1
        assert calls[0].column >= 0


class TestRustUnwrapAnalyzerTestAwareness:
    """Tests for test-aware detection."""

    def test_detects_call_inside_test(self) -> None:
        """Should mark calls inside #[test] functions."""
        analyzer = RustUnwrapAnalyzer()
        code = """
#[test]
fn test_something() {
    let x = foo().unwrap();
}
"""
        calls = analyzer.find_unwrap_calls(code)
        assert len(calls) == 1
        assert calls[0].is_in_test is True

    def test_detects_call_inside_cfg_test(self) -> None:
        """Should mark calls inside #[cfg(test)] modules."""
        analyzer = RustUnwrapAnalyzer()
        code = """
#[cfg(test)]
mod tests {
    fn test_helper() {
        let x = foo().unwrap();
    }
}
"""
        calls = analyzer.find_unwrap_calls(code)
        assert len(calls) == 1
        assert calls[0].is_in_test is True

    def test_non_test_code_not_marked(self) -> None:
        """Should not mark calls in regular functions as test code."""
        analyzer = RustUnwrapAnalyzer()
        code = """
fn regular_function() {
    let x = foo().unwrap();
}
"""
        calls = analyzer.find_unwrap_calls(code)
        assert len(calls) == 1
        assert calls[0].is_in_test is False


class TestRustUnwrapAnalyzerContext:
    """Tests for code context extraction."""

    def test_extracts_context_line(self) -> None:
        """Should extract the code line as context."""
        analyzer = RustUnwrapAnalyzer()
        code = """fn main() {
    let x = some_function().unwrap();
}
"""
        calls = analyzer.find_unwrap_calls(code)
        assert len(calls) == 1
        assert "unwrap" in calls[0].context


class TestRustUnwrapAnalyzerEdgeCases:
    """Tests for edge cases."""

    def test_empty_code(self) -> None:
        """Should handle empty code gracefully."""
        analyzer = RustUnwrapAnalyzer()
        calls = analyzer.find_unwrap_calls("")
        assert len(calls) == 0

    def test_no_functions(self) -> None:
        """Should handle code with no functions."""
        analyzer = RustUnwrapAnalyzer()
        code = "// Just a comment"
        calls = analyzer.find_unwrap_calls(code)
        assert len(calls) == 0

    def test_chained_unwrap(self) -> None:
        """Should detect unwrap in method chains."""
        analyzer = RustUnwrapAnalyzer()
        code = """
fn main() {
    let x = some_map.get("key").unwrap().parse::<i32>().unwrap();
}
"""
        calls = analyzer.find_unwrap_calls(code)
        assert len(calls) == 2

    def test_unwrap_without_tree_sitter(self) -> None:
        """Should return empty when tree-sitter not available."""
        analyzer = RustUnwrapAnalyzer()
        # Save and mock tree_sitter_available
        original = analyzer.tree_sitter_available
        analyzer.tree_sitter_available = False

        calls = analyzer.find_unwrap_calls("fn main() { foo().unwrap(); }")
        assert len(calls) == 0

        analyzer.tree_sitter_available = original

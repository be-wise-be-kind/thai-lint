"""
Purpose: Unit tests for RustCloneAnalyzer detection logic

Scope: Tests for clone-in-loop, clone-chain, and unnecessary-clone pattern detection

Overview: Comprehensive test suite for the RustCloneAnalyzer class covering all three
    detection patterns: clone calls inside loop bodies (for, while, loop), chained clone
    calls (.clone().clone()), and unnecessary clones (clone before move where source is
    unused). Validates line/column info, test-awareness, context extraction, edge cases,
    and negative cases (necessary clones not flagged, field access not flagged).

Dependencies: pytest, src.analyzers.rust_base, src.linters.clone_abuse.rust_analyzer

Exports: Test classes for each detection pattern and edge case category

Interfaces: Standard pytest test classes

Implementation: Direct analyzer instantiation with sample Rust code strings
"""

import pytest

from src.analyzers.rust_base import TREE_SITTER_RUST_AVAILABLE
from src.linters.clone_abuse.rust_analyzer import RustCloneAnalyzer

pytestmark = pytest.mark.skipif(
    not TREE_SITTER_RUST_AVAILABLE, reason="tree-sitter-rust not installed"
)


class TestCloneInLoopDetection:
    """Tests for clone-in-loop pattern detection."""

    def test_detects_clone_in_for_loop(self) -> None:
        """Should detect clone call inside a for loop."""
        analyzer = RustCloneAnalyzer()
        code = """
fn process(items: &[String]) {
    for item in items {
        let copy = item.clone();
        do_something(copy);
    }
}
"""
        calls = analyzer.find_clone_calls(code)
        loop_calls = [c for c in calls if c.pattern == "clone-in-loop"]
        assert len(loop_calls) == 1

    def test_detects_clone_in_while_loop(self) -> None:
        """Should detect clone call inside a while loop."""
        analyzer = RustCloneAnalyzer()
        code = """
fn process(data: &String) {
    let mut count = 0;
    while count < 10 {
        let copy = data.clone();
        use_data(copy);
        count += 1;
    }
}
"""
        calls = analyzer.find_clone_calls(code)
        loop_calls = [c for c in calls if c.pattern == "clone-in-loop"]
        assert len(loop_calls) == 1

    def test_detects_clone_in_infinite_loop(self) -> None:
        """Should detect clone call inside an infinite loop."""
        analyzer = RustCloneAnalyzer()
        code = """
fn process(data: &String) {
    loop {
        let copy = data.clone();
        if should_stop(copy) {
            break;
        }
    }
}
"""
        calls = analyzer.find_clone_calls(code)
        loop_calls = [c for c in calls if c.pattern == "clone-in-loop"]
        assert len(loop_calls) == 1

    def test_no_false_positive_outside_loop(self) -> None:
        """Should not flag clone outside a loop as clone-in-loop."""
        analyzer = RustCloneAnalyzer()
        code = """
fn process(data: &String) {
    let copy = data.clone();
    use_data(copy);
}
"""
        calls = analyzer.find_clone_calls(code)
        loop_calls = [c for c in calls if c.pattern == "clone-in-loop"]
        assert len(loop_calls) == 0


class TestCloneChainDetection:
    """Tests for clone-chain pattern detection."""

    def test_detects_clone_chain(self) -> None:
        """Should detect chained clone calls like .clone().clone()."""
        analyzer = RustCloneAnalyzer()
        code = """
fn process(data: &String) {
    let redundant = data.clone().clone();
    use_data(redundant);
}
"""
        calls = analyzer.find_clone_calls(code)
        chain_calls = [c for c in calls if c.pattern == "clone-chain"]
        assert len(chain_calls) >= 1

    def test_single_clone_not_flagged_as_chain(self) -> None:
        """Should not flag a single clone call as a clone chain."""
        analyzer = RustCloneAnalyzer()
        code = """
fn process(data: &String) {
    let copy = data.clone();
    use_data(copy);
}
"""
        calls = analyzer.find_clone_calls(code)
        chain_calls = [c for c in calls if c.pattern == "clone-chain"]
        assert len(chain_calls) == 0


class TestUnnecessaryCloneDetection:
    """Tests for unnecessary-clone pattern detection."""

    def test_detects_clone_before_move(self) -> None:
        """Should detect unnecessary clone before a move."""
        analyzer = RustCloneAnalyzer()
        code = """
fn process(data: String) {
    let copy = data.clone();
    consume(copy);
}
"""
        calls = analyzer.find_clone_calls(code)
        unnecessary = [c for c in calls if c.pattern == "unnecessary-clone"]
        assert len(unnecessary) == 1

    def test_necessary_clone_not_flagged(self) -> None:
        """Should not flag clone when the source is used after cloning."""
        analyzer = RustCloneAnalyzer()
        code = """
fn process(data: &String) {
    let copy = data.clone();
    use_data(copy);
    println!("{}", data);
}
"""
        calls = analyzer.find_clone_calls(code)
        unnecessary = [c for c in calls if c.pattern == "unnecessary-clone"]
        assert len(unnecessary) == 0

    def test_field_access_not_flagged_as_unnecessary(self) -> None:
        """Should not flag field access clone as unnecessary."""
        analyzer = RustCloneAnalyzer()
        code = """
fn process(container: &Container) {
    let copy = container.data.clone();
    use_data(copy);
}
"""
        calls = analyzer.find_clone_calls(code)
        unnecessary = [c for c in calls if c.pattern == "unnecessary-clone"]
        assert len(unnecessary) == 0


class TestCloneAnalyzerLineInfo:
    """Tests for correct line and column reporting."""

    def test_correct_line_for_clone_in_loop(self) -> None:
        """Should report the correct line number for clone in a loop."""
        analyzer = RustCloneAnalyzer()
        code = """fn main() {
    let data = String::from("hello");
    for _i in 0..10 {
        let copy = data.clone();
    }
}
"""
        calls = analyzer.find_clone_calls(code)
        assert len(calls) >= 1
        clone_call = calls[0]
        assert clone_call.line == 4

    def test_correct_column_is_non_negative(self) -> None:
        """Should report a non-negative column number for clone calls."""
        analyzer = RustCloneAnalyzer()
        code = "fn main() { let x = data.clone(); }"
        calls = analyzer.find_clone_calls(code)
        assert len(calls) >= 1
        assert calls[0].column >= 0


class TestCloneAnalyzerTestAwareness:
    """Tests for test code detection."""

    def test_detects_clone_in_test_function(self) -> None:
        """Should mark clone calls inside a #[test] function as test code."""
        analyzer = RustCloneAnalyzer()
        code = """
#[test]
fn test_something() {
    let items = vec![String::from("test")];
    for item in &items {
        let copy = item.clone();
        do_something(copy);
    }
}
"""
        calls = analyzer.find_clone_calls(code)
        assert len(calls) >= 1
        assert all(c.is_in_test for c in calls)

    def test_detects_clone_in_cfg_test(self) -> None:
        """Should mark clone calls inside a #[cfg(test)] module as test code."""
        analyzer = RustCloneAnalyzer()
        code = """
#[cfg(test)]
mod tests {
    fn test_helper() {
        let items = vec![String::from("test")];
        for item in &items {
            let copy = item.clone();
            do_something(copy);
        }
    }
}
"""
        calls = analyzer.find_clone_calls(code)
        assert len(calls) >= 1
        assert all(c.is_in_test for c in calls)

    def test_non_test_code_not_marked(self) -> None:
        """Should not mark clone calls in non-test code as test code."""
        analyzer = RustCloneAnalyzer()
        code = """
fn regular_function() {
    let data = String::from("hello");
    let copy = data.clone();
}
"""
        calls = analyzer.find_clone_calls(code)
        assert len(calls) >= 1
        assert all(not c.is_in_test for c in calls)


class TestCloneAnalyzerContext:
    """Tests for code context extraction."""

    def test_extracts_context_line(self) -> None:
        """Should extract a context line containing the clone call."""
        analyzer = RustCloneAnalyzer()
        code = """fn main() {
    let x = some_data.clone();
}
"""
        calls = analyzer.find_clone_calls(code)
        assert len(calls) >= 1
        assert "clone" in calls[0].context


class TestCloneAnalyzerEdgeCases:
    """Tests for edge cases."""

    def test_empty_code(self) -> None:
        """Should return no findings for empty code input."""
        analyzer = RustCloneAnalyzer()
        calls = analyzer.find_clone_calls("")
        assert len(calls) == 0

    def test_no_clones(self) -> None:
        """Should return no findings when code contains no clone calls."""
        analyzer = RustCloneAnalyzer()
        code = """
fn process(data: &str) {
    let borrowed = data;
    println!("{}", borrowed);
}
"""
        calls = analyzer.find_clone_calls(code)
        assert len(calls) == 0

    def test_clone_without_tree_sitter(self) -> None:
        """Should return no findings when tree-sitter is unavailable."""
        analyzer = RustCloneAnalyzer()
        original = analyzer.tree_sitter_available
        analyzer.tree_sitter_available = False
        calls = analyzer.find_clone_calls("fn main() { data.clone(); }")
        assert len(calls) == 0
        analyzer.tree_sitter_available = original

    def test_multiple_patterns_detected(self) -> None:
        """Should detect multiple distinct patterns in the same code."""
        analyzer = RustCloneAnalyzer()
        code = """
fn process(items: &[String], data: &String) {
    for item in items {
        let copy = item.clone();
        do_something(copy);
    }
    let redundant = data.clone().clone();
    use_data(redundant);
}
"""
        calls = analyzer.find_clone_calls(code)
        patterns = {c.pattern for c in calls}
        assert "clone-in-loop" in patterns
        assert "clone-chain" in patterns

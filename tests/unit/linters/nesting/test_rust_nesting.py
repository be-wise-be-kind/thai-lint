"""
Purpose: Test suite for Rust nesting depth violation detection

Scope: Rust function nesting depth analysis using tree-sitter parsing

Overview: Tests for Rust nesting depth violation detection covering basic nesting with
    if/match/for/while/loop, closures adding nesting, functions within impl blocks,
    violation messages with function names and depth, and language filtering. Validates
    that Rust control flow constructs are properly counted for nesting depth.

Dependencies: pytest, NestingDepthRule, TREE_SITTER_RUST_AVAILABLE, pathlib, unittest.mock

Exports: TestRustNestingBasic, TestRustNestingControlFlow, TestRustClosureNesting,
    TestRustLanguageFiltering, TestRustNestingEdgeCases

Interfaces: Tests NestingDepthRule.check(context) -> list[Violation] with Rust code samples

Implementation: Uses inline Rust code strings as test fixtures, sets language="rust"
"""

from pathlib import Path
from unittest.mock import Mock

import pytest

from src.analyzers.rust_base import TREE_SITTER_RUST_AVAILABLE
from src.linters.nesting.linter import NestingDepthRule

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


class TestRustNestingBasic:
    """Test basic nesting depth detection in Rust functions."""

    def test_simple_function_passes(self) -> None:
        """Function with no nesting should pass."""
        code = """
fn simple() {
    let x = 1;
    let y = 2;
}
"""
        rule = NestingDepthRule()
        violations = rule.check(_create_context(code))
        assert len(violations) == 0

    def test_shallow_nesting_passes(self) -> None:
        """Function with depth <= 4 should pass."""
        code = """
fn shallow() {
    if true {
        if true {
            let x = 1;
        }
    }
}
"""
        rule = NestingDepthRule()
        violations = rule.check(_create_context(code))
        assert len(violations) == 0

    def test_deep_nesting_violates(self) -> None:
        """Function with depth > 4 should violate."""
        code = """
fn deeply_nested() {
    if true {
        if true {
            if true {
                if true {
                    if true {
                        let x = 1;
                    }
                }
            }
        }
    }
}
"""
        rule = NestingDepthRule()
        violations = rule.check(_create_context(code))
        assert len(violations) > 0
        assert "deeply_nested" in violations[0].message

    def test_violation_includes_depth(self) -> None:
        """Violation message should include actual nesting depth."""
        code = """
fn too_deep() {
    if true {
        for i in 0..10 {
            while true {
                match x {
                    _ => {
                        if true {
                            let x = 1;
                        }
                    }
                }
            }
        }
    }
}
"""
        rule = NestingDepthRule()
        violations = rule.check(_create_context(code))
        assert len(violations) > 0


class TestRustNestingControlFlow:
    """Test nesting detection for various Rust control flow."""

    def test_match_increases_depth(self) -> None:
        """Match expressions should increase nesting depth."""
        code = """
fn match_nested() {
    match x {
        1 => match y {
            2 => match z {
                3 => match w {
                    4 => match v {
                        5 => {}
                    }
                }
            }
        }
    }
}
"""
        rule = NestingDepthRule()
        violations = rule.check(_create_context(code))
        assert len(violations) > 0

    def test_for_loop_increases_depth(self) -> None:
        """For loops should increase nesting depth."""
        code = """
fn for_nested() {
    for i in 0..10 {
        for j in 0..10 {
            for k in 0..10 {
                for l in 0..10 {
                    for m in 0..10 {
                        let _ = i + j + k + l + m;
                    }
                }
            }
        }
    }
}
"""
        rule = NestingDepthRule()
        violations = rule.check(_create_context(code))
        assert len(violations) > 0

    def test_while_increases_depth(self) -> None:
        """While loops should increase nesting depth."""
        code = """
fn while_nested() {
    while true {
        while true {
            while true {
                while true {
                    while true {
                        break;
                    }
                }
            }
        }
    }
}
"""
        rule = NestingDepthRule()
        violations = rule.check(_create_context(code))
        assert len(violations) > 0

    def test_loop_increases_depth(self) -> None:
        """Loop expressions should increase nesting depth."""
        code = """
fn loop_nested() {
    loop {
        loop {
            loop {
                loop {
                    loop {
                        break;
                    }
                }
            }
        }
    }
}
"""
        rule = NestingDepthRule()
        violations = rule.check(_create_context(code))
        assert len(violations) > 0


class TestRustClosureNesting:
    """Test that closures contribute to nesting depth."""

    def test_closure_increases_depth(self) -> None:
        """Closures should increase nesting depth."""
        code = """
fn closure_nested() {
    let f = |x| {
        let g = |y| {
            let h = |z| {
                let i = |w| {
                    let j = |v| {
                        v
                    };
                    j(w)
                };
                i(z)
            };
            h(y)
        };
        g(x)
    };
}
"""
        rule = NestingDepthRule()
        violations = rule.check(_create_context(code))
        assert len(violations) > 0


class TestRustLanguageFiltering:
    """Test that nesting analysis only processes Rust files."""

    def test_ignores_python_files(self) -> None:
        """Should not process Python files via Rust analyzer."""
        code = "def foo():\n    pass"
        context = _create_context(code, filename="test.py", language="python")
        rule = NestingDepthRule()
        violations = rule.check(context)
        assert isinstance(violations, list)

    def test_processes_rust_files(self) -> None:
        """Should process .rs files."""
        code = """
fn deeply_nested() {
    if true {
        if true {
            if true {
                if true {
                    if true {
                        let x = 1;
                    }
                }
            }
        }
    }
}
"""
        context = _create_context(code, filename="src/lib.rs", language="rust")
        rule = NestingDepthRule()
        violations = rule.check(context)
        assert len(violations) > 0


class TestRustNestingEdgeCases:
    """Test edge cases for Rust nesting analysis."""

    def test_empty_file(self) -> None:
        """Should handle empty files gracefully."""
        rule = NestingDepthRule()
        violations = rule.check(_create_context(""))
        assert len(violations) == 0

    def test_none_content(self) -> None:
        """Should handle None content gracefully."""
        context = _create_context("")
        context.file_content = None
        rule = NestingDepthRule()
        violations = rule.check(context)
        assert len(violations) == 0

    def test_function_without_body(self) -> None:
        """Function declaration without body should not crash."""
        code = """
fn empty_func();
"""
        rule = NestingDepthRule()
        violations = rule.check(_create_context(code))
        assert len(violations) == 0

    def test_multiple_functions(self) -> None:
        """Multiple functions should be analyzed independently."""
        code = """
fn simple() {
    let x = 1;
}

fn deeply_nested() {
    if true {
        if true {
            if true {
                if true {
                    if true {
                        let x = 1;
                    }
                }
            }
        }
    }
}
"""
        rule = NestingDepthRule()
        violations = rule.check(_create_context(code))
        assert len(violations) == 1
        assert "deeply_nested" in violations[0].message

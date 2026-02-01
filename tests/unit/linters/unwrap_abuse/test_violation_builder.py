"""
Purpose: Unit tests for unwrap abuse violation builder functions

Scope: Tests for build_unwrap_violation and build_expect_violation functions

Overview: Tests that violation builder functions produce correctly structured Violation
    objects with appropriate rule IDs, messages, suggestions, and location information.
    Verifies that unwrap violations use "unwrap-abuse.unwrap-call" rule ID and expect
    violations use "unwrap-abuse.expect-call" rule ID.

Dependencies: pytest, violation_builder functions

Exports: Test classes for violation builder behavior

Interfaces: Standard pytest test methods

Implementation: Direct function testing with assertions on Violation fields
"""

from src.linters.unwrap_abuse.violation_builder import (
    build_expect_violation,
    build_unwrap_violation,
)


class TestBuildUnwrapViolation:
    """Tests for build_unwrap_violation function."""

    def test_rule_id(self) -> None:
        """Should use unwrap-abuse.unwrap-call rule ID."""
        violation = build_unwrap_violation("main.rs", 10, 4, "foo().unwrap()")
        assert violation.rule_id == "unwrap-abuse.unwrap-call"

    def test_file_path(self) -> None:
        """Should include file path."""
        violation = build_unwrap_violation("src/lib.rs", 5, 0, "context")
        assert violation.file_path == "src/lib.rs"

    def test_line_number(self) -> None:
        """Should include line number."""
        violation = build_unwrap_violation("main.rs", 42, 0, "context")
        assert violation.line == 42

    def test_column_number(self) -> None:
        """Should include column number."""
        violation = build_unwrap_violation("main.rs", 1, 8, "context")
        assert violation.column == 8

    def test_message_contains_unwrap(self) -> None:
        """Should mention .unwrap() in message."""
        violation = build_unwrap_violation("main.rs", 1, 0, "foo().unwrap()")
        assert ".unwrap()" in violation.message

    def test_message_contains_context(self) -> None:
        """Should include code context in message."""
        violation = build_unwrap_violation("main.rs", 1, 0, "let x = foo().unwrap();")
        assert "let x = foo().unwrap();" in violation.message

    def test_suggestion_mentions_question_mark(self) -> None:
        """Should suggest the ? operator."""
        violation = build_unwrap_violation("main.rs", 1, 0, "context")
        assert "?" in (violation.suggestion or "")

    def test_suggestion_mentions_unwrap_or(self) -> None:
        """Should suggest unwrap_or alternatives."""
        violation = build_unwrap_violation("main.rs", 1, 0, "context")
        assert "unwrap_or" in (violation.suggestion or "")


class TestBuildExpectViolation:
    """Tests for build_expect_violation function."""

    def test_rule_id(self) -> None:
        """Should use unwrap-abuse.expect-call rule ID."""
        violation = build_expect_violation("main.rs", 10, 4, 'foo().expect("msg")')
        assert violation.rule_id == "unwrap-abuse.expect-call"

    def test_file_path(self) -> None:
        """Should include file path."""
        violation = build_expect_violation("src/lib.rs", 5, 0, "context")
        assert violation.file_path == "src/lib.rs"

    def test_line_number(self) -> None:
        """Should include line number."""
        violation = build_expect_violation("main.rs", 42, 0, "context")
        assert violation.line == 42

    def test_message_contains_expect(self) -> None:
        """Should mention .expect() in message."""
        violation = build_expect_violation("main.rs", 1, 0, 'bar().expect("msg")')
        assert ".expect()" in violation.message

    def test_suggestion_mentions_question_mark(self) -> None:
        """Should suggest the ? operator."""
        violation = build_expect_violation("main.rs", 1, 0, "context")
        assert "?" in (violation.suggestion or "")

    def test_suggestion_mentions_context_method(self) -> None:
        """Should suggest .context() for better error handling."""
        violation = build_expect_violation("main.rs", 1, 0, "context")
        assert "context()" in (violation.suggestion or "")

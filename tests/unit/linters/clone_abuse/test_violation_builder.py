"""
Purpose: Unit tests for clone abuse violation builder factory functions

Scope: Tests for build_clone_in_loop_violation, build_clone_chain_violation,
    and build_unnecessary_clone_violation

Overview: Validates that each violation builder produces correct rule IDs, messages,
    file paths, line numbers, column numbers, and actionable suggestions. Each violation
    type has pattern-specific messaging and suggestions for safer Rust alternatives.

Dependencies: src.linters.clone_abuse.violation_builder

Exports: TestBuildCloneInLoopViolation, TestBuildCloneChainViolation, TestBuildUnnecessaryCloneViolation

Interfaces: Standard pytest test classes

Implementation: Direct function calls with assertion-based validation
"""

from src.linters.clone_abuse.violation_builder import (
    build_clone_chain_violation,
    build_clone_in_loop_violation,
    build_unnecessary_clone_violation,
)


class TestBuildCloneInLoopViolation:
    """Tests for clone-in-loop violation builder."""

    def test_rule_id(self) -> None:
        """Should have correct rule_id for clone-in-loop."""
        violation = build_clone_in_loop_violation("main.rs", 10, 4, "item.clone()")
        assert violation.rule_id == "clone-abuse.clone-in-loop"

    def test_file_path(self) -> None:
        """Should include file path in violation."""
        violation = build_clone_in_loop_violation("src/lib.rs", 5, 0, "context")
        assert violation.file_path == "src/lib.rs"

    def test_line_number(self) -> None:
        """Should include correct line number."""
        violation = build_clone_in_loop_violation("main.rs", 42, 0, "context")
        assert violation.line == 42

    def test_column_number(self) -> None:
        """Should include correct column number."""
        violation = build_clone_in_loop_violation("main.rs", 1, 8, "context")
        assert violation.column == 8

    def test_message_contains_clone(self) -> None:
        """Should mention .clone() in the message."""
        violation = build_clone_in_loop_violation("main.rs", 1, 0, "item.clone()")
        assert ".clone()" in violation.message

    def test_message_contains_loop(self) -> None:
        """Should mention loop in the message."""
        violation = build_clone_in_loop_violation("main.rs", 1, 0, "item.clone()")
        assert "loop" in violation.message.lower()

    def test_suggestion_present(self) -> None:
        """Should provide a non-empty suggestion."""
        violation = build_clone_in_loop_violation("main.rs", 1, 0, "context")
        assert violation.suggestion is not None
        assert len(violation.suggestion) > 0


class TestBuildCloneChainViolation:
    """Tests for clone-chain violation builder."""

    def test_rule_id(self) -> None:
        """Should have correct rule_id for clone-chain."""
        violation = build_clone_chain_violation("main.rs", 10, 4, "data.clone().clone()")
        assert violation.rule_id == "clone-abuse.clone-chain"

    def test_file_path(self) -> None:
        """Should include file path in violation."""
        violation = build_clone_chain_violation("src/lib.rs", 5, 0, "context")
        assert violation.file_path == "src/lib.rs"

    def test_line_number(self) -> None:
        """Should include correct line number."""
        violation = build_clone_chain_violation("main.rs", 42, 0, "context")
        assert violation.line == 42

    def test_message_contains_clone(self) -> None:
        """Should mention clone in the message."""
        violation = build_clone_chain_violation("main.rs", 1, 0, "data.clone().clone()")
        assert "clone" in violation.message.lower()

    def test_suggestion_present(self) -> None:
        """Should provide a non-empty suggestion."""
        violation = build_clone_chain_violation("main.rs", 1, 0, "context")
        assert violation.suggestion is not None
        assert len(violation.suggestion) > 0


class TestBuildUnnecessaryCloneViolation:
    """Tests for unnecessary-clone violation builder."""

    def test_rule_id(self) -> None:
        """Should have correct rule_id for unnecessary-clone."""
        violation = build_unnecessary_clone_violation("main.rs", 10, 4, "data.clone()")
        assert violation.rule_id == "clone-abuse.unnecessary-clone"

    def test_file_path(self) -> None:
        """Should include file path in violation."""
        violation = build_unnecessary_clone_violation("src/lib.rs", 5, 0, "context")
        assert violation.file_path == "src/lib.rs"

    def test_line_number(self) -> None:
        """Should include correct line number."""
        violation = build_unnecessary_clone_violation("main.rs", 42, 0, "context")
        assert violation.line == 42

    def test_message_contains_clone(self) -> None:
        """Should mention clone in the message."""
        violation = build_unnecessary_clone_violation("main.rs", 1, 0, "data.clone()")
        assert "clone" in violation.message.lower()

    def test_suggestion_present(self) -> None:
        """Should provide a non-empty suggestion."""
        violation = build_unnecessary_clone_violation("main.rs", 1, 0, "context")
        assert violation.suggestion is not None
        assert len(violation.suggestion) > 0

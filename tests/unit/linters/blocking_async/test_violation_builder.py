"""
Purpose: Unit tests for blocking-in-async violation builder factory functions

Scope: Tests for build_fs_in_async_violation, build_sleep_in_async_violation,
    and build_net_in_async_violation

Overview: Validates that each violation builder produces correct rule IDs, messages,
    file paths, line numbers, column numbers, and actionable suggestions. Each violation
    type has pattern-specific messaging and suggestions for async-compatible Rust alternatives.

Dependencies: src.linters.blocking_async.violation_builder

Exports: TestBuildFsInAsyncViolation, TestBuildSleepInAsyncViolation,
    TestBuildNetInAsyncViolation

Interfaces: Standard pytest test classes

Implementation: Direct function calls with assertion-based validation
"""

from src.linters.blocking_async.violation_builder import (
    build_fs_in_async_violation,
    build_net_in_async_violation,
    build_sleep_in_async_violation,
)


class TestBuildFsInAsyncViolation:
    """Tests for fs-in-async violation builder."""

    def test_rule_id(self) -> None:
        """Should have correct rule_id for fs-in-async."""
        violation = build_fs_in_async_violation("main.rs", 10, 4, "std::fs::read_to_string")
        assert violation.rule_id == "blocking-async.fs-in-async"

    def test_file_path(self) -> None:
        """Should include file path in violation."""
        violation = build_fs_in_async_violation("src/lib.rs", 5, 0, "context")
        assert violation.file_path == "src/lib.rs"

    def test_line_number(self) -> None:
        """Should include correct line number."""
        violation = build_fs_in_async_violation("main.rs", 42, 0, "context")
        assert violation.line == 42

    def test_column_number(self) -> None:
        """Should include correct column number."""
        violation = build_fs_in_async_violation("main.rs", 1, 8, "context")
        assert violation.column == 8

    def test_message_contains_fs(self) -> None:
        """Should mention std::fs in the message."""
        violation = build_fs_in_async_violation("main.rs", 1, 0, "std::fs::read_to_string")
        assert "std::fs" in violation.message

    def test_message_contains_async(self) -> None:
        """Should mention async in the message."""
        violation = build_fs_in_async_violation("main.rs", 1, 0, "context")
        assert "async" in violation.message.lower()

    def test_suggestion_present(self) -> None:
        """Should provide a non-empty suggestion."""
        violation = build_fs_in_async_violation("main.rs", 1, 0, "context")
        assert violation.suggestion is not None
        assert len(violation.suggestion) > 0

    def test_suggestion_mentions_tokio(self) -> None:
        """Should suggest tokio::fs as alternative."""
        violation = build_fs_in_async_violation("main.rs", 1, 0, "context")
        assert "tokio::fs" in violation.suggestion


class TestBuildSleepInAsyncViolation:
    """Tests for sleep-in-async violation builder."""

    def test_rule_id(self) -> None:
        """Should have correct rule_id for sleep-in-async."""
        violation = build_sleep_in_async_violation("main.rs", 10, 4, "std::thread::sleep")
        assert violation.rule_id == "blocking-async.sleep-in-async"

    def test_file_path(self) -> None:
        """Should include file path in violation."""
        violation = build_sleep_in_async_violation("src/lib.rs", 5, 0, "context")
        assert violation.file_path == "src/lib.rs"

    def test_line_number(self) -> None:
        """Should include correct line number."""
        violation = build_sleep_in_async_violation("main.rs", 42, 0, "context")
        assert violation.line == 42

    def test_message_contains_sleep(self) -> None:
        """Should mention sleep in the message."""
        violation = build_sleep_in_async_violation("main.rs", 1, 0, "std::thread::sleep")
        assert "sleep" in violation.message.lower()

    def test_suggestion_present(self) -> None:
        """Should provide a non-empty suggestion."""
        violation = build_sleep_in_async_violation("main.rs", 1, 0, "context")
        assert violation.suggestion is not None
        assert len(violation.suggestion) > 0

    def test_suggestion_mentions_tokio_time(self) -> None:
        """Should suggest tokio::time::sleep as alternative."""
        violation = build_sleep_in_async_violation("main.rs", 1, 0, "context")
        assert "tokio::time::sleep" in violation.suggestion


class TestBuildNetInAsyncViolation:
    """Tests for net-in-async violation builder."""

    def test_rule_id(self) -> None:
        """Should have correct rule_id for net-in-async."""
        violation = build_net_in_async_violation("main.rs", 10, 4, "std::net::TcpStream")
        assert violation.rule_id == "blocking-async.net-in-async"

    def test_file_path(self) -> None:
        """Should include file path in violation."""
        violation = build_net_in_async_violation("src/lib.rs", 5, 0, "context")
        assert violation.file_path == "src/lib.rs"

    def test_line_number(self) -> None:
        """Should include correct line number."""
        violation = build_net_in_async_violation("main.rs", 42, 0, "context")
        assert violation.line == 42

    def test_message_contains_net(self) -> None:
        """Should mention std::net in the message."""
        violation = build_net_in_async_violation("main.rs", 1, 0, "std::net::TcpStream")
        assert "std::net" in violation.message

    def test_suggestion_present(self) -> None:
        """Should provide a non-empty suggestion."""
        violation = build_net_in_async_violation("main.rs", 1, 0, "context")
        assert violation.suggestion is not None
        assert len(violation.suggestion) > 0

    def test_suggestion_mentions_tokio_net(self) -> None:
        """Should suggest tokio::net as alternative."""
        violation = build_net_in_async_violation("main.rs", 1, 0, "context")
        assert "tokio::net" in violation.suggestion

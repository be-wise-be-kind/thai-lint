"""
Purpose: Tests for CQS violation message building

Scope: Unit tests for violation message formatting and suggestion generation

Overview: Test suite for CQS violation building. Tests the creation of violation
    messages with proper formatting, including function names, class context for methods,
    line numbers for INPUT and OUTPUT operations, and actionable suggestions for fixing
    violations.

Dependencies: pytest, src.linters.cqs

Exports: Test classes for violation building

Interfaces: pytest test discovery and execution

Implementation: Tests using build_cqs_violation function
"""

from src.linters.cqs import build_cqs_violation
from src.linters.cqs.types import CQSPattern, InputOperation, OutputOperation


class TestViolationMessageFormat:
    """Tests for violation message formatting."""

    def test_message_includes_function_name(self) -> None:
        """Violation message includes the function name."""
        pattern = CQSPattern(
            function_name="process_and_save",
            line=1,
            column=0,
            file_path="test.py",
            inputs=[InputOperation(2, 4, "fetch_data()", "data")],
            outputs=[OutputOperation(3, 4, "save_to_db(data)")],
        )
        violation = build_cqs_violation(pattern)
        assert "process_and_save" in violation.message

    def test_message_includes_class_name_for_method(self) -> None:
        """Violation message includes class name for methods."""
        pattern = CQSPattern(
            function_name="process",
            line=5,
            column=4,
            file_path="test.py",
            inputs=[InputOperation(6, 8, "self.load_data()", "self.data")],
            outputs=[OutputOperation(7, 8, "self.persist()")],
            is_method=True,
            class_name="DataProcessor",
        )
        violation = build_cqs_violation(pattern)
        assert "DataProcessor.process" in violation.message

    def test_message_includes_file_path(self) -> None:
        """Violation message includes file path."""
        pattern = CQSPattern(
            function_name="mixed",
            line=10,
            column=0,
            file_path="src/services/processor.py",
            inputs=[InputOperation(11, 4, "query()", "x")],
            outputs=[OutputOperation(12, 4, "command(x)")],
        )
        violation = build_cqs_violation(pattern)
        assert violation.file_path == "src/services/processor.py"

    def test_message_includes_line_number(self) -> None:
        """Violation message includes function line number."""
        pattern = CQSPattern(
            function_name="mixed",
            line=42,
            column=0,
            file_path="test.py",
            inputs=[InputOperation(43, 4, "query()", "x")],
            outputs=[OutputOperation(44, 4, "command(x)")],
        )
        violation = build_cqs_violation(pattern)
        assert violation.line == 42


class TestViolationInputDetails:
    """Tests for INPUT operation details in violations."""

    def test_message_lists_input_operations(self) -> None:
        """Violation message lists INPUT operations."""
        pattern = CQSPattern(
            function_name="mixed",
            line=1,
            column=0,
            file_path="test.py",
            inputs=[InputOperation(2, 4, "fetch_data(id)", "data")],
            outputs=[OutputOperation(3, 4, "save(data)")],
        )
        violation = build_cqs_violation(pattern)
        message = violation.message
        assert "INPUT" in message
        assert "fetch_data" in message

    def test_message_includes_input_line_numbers(self) -> None:
        """Violation message includes line numbers for INPUTs."""
        pattern = CQSPattern(
            function_name="mixed",
            line=1,
            column=0,
            file_path="test.py",
            inputs=[InputOperation(47, 4, "query()", "x")],
            outputs=[OutputOperation(48, 4, "command()")],
        )
        violation = build_cqs_violation(pattern)
        assert "47" in violation.message

    def test_message_lists_multiple_inputs(self) -> None:
        """Violation message lists multiple INPUT operations."""
        pattern = CQSPattern(
            function_name="mixed",
            line=1,
            column=0,
            file_path="test.py",
            inputs=[
                InputOperation(2, 4, "get_user(id)", "user"),
                InputOperation(3, 4, "load_settings()", "settings"),
            ],
            outputs=[OutputOperation(4, 4, "save()")],
        )
        violation = build_cqs_violation(pattern)
        assert "get_user" in violation.message
        assert "load_settings" in violation.message


class TestViolationOutputDetails:
    """Tests for OUTPUT operation details in violations."""

    def test_message_lists_output_operations(self) -> None:
        """Violation message lists OUTPUT operations."""
        pattern = CQSPattern(
            function_name="mixed",
            line=1,
            column=0,
            file_path="test.py",
            inputs=[InputOperation(2, 4, "query()", "x")],
            outputs=[OutputOperation(3, 4, "save_to_db(data)")],
        )
        violation = build_cqs_violation(pattern)
        message = violation.message
        assert "OUTPUT" in message
        assert "save_to_db" in message

    def test_message_includes_output_line_numbers(self) -> None:
        """Violation message includes line numbers for OUTPUTs."""
        pattern = CQSPattern(
            function_name="mixed",
            line=1,
            column=0,
            file_path="test.py",
            inputs=[InputOperation(47, 4, "query()", "x")],
            outputs=[OutputOperation(50, 4, "command()")],
        )
        violation = build_cqs_violation(pattern)
        assert "50" in violation.message

    def test_message_lists_multiple_outputs(self) -> None:
        """Violation message lists multiple OUTPUT operations."""
        pattern = CQSPattern(
            function_name="mixed",
            line=1,
            column=0,
            file_path="test.py",
            inputs=[InputOperation(2, 4, "query()", "x")],
            outputs=[
                OutputOperation(3, 4, "update_user(user)"),
                OutputOperation(4, 4, "notify_admin()"),
            ],
        )
        violation = build_cqs_violation(pattern)
        assert "update_user" in violation.message
        assert "notify_admin" in violation.message


class TestViolationSuggestion:
    """Tests for violation suggestions."""

    def test_suggestion_recommends_splitting(self) -> None:
        """Violation includes suggestion to split function."""
        pattern = CQSPattern(
            function_name="process_and_save",
            line=1,
            column=0,
            file_path="test.py",
            inputs=[InputOperation(2, 4, "fetch()", "data")],
            outputs=[OutputOperation(3, 4, "save(data)")],
        )
        violation = build_cqs_violation(pattern)
        suggestion = violation.suggestion or violation.message
        assert "split" in suggestion.lower() or "separate" in suggestion.lower()

    def test_suggestion_mentions_query_and_command(self) -> None:
        """Suggestion mentions query and command functions."""
        pattern = CQSPattern(
            function_name="mixed",
            line=1,
            column=0,
            file_path="test.py",
            inputs=[InputOperation(2, 4, "fetch()", "x")],
            outputs=[OutputOperation(3, 4, "save(x)")],
        )
        violation = build_cqs_violation(pattern)
        suggestion = violation.suggestion or violation.message
        assert "query" in suggestion.lower() or "command" in suggestion.lower()


class TestViolationSeverity:
    """Tests for violation severity."""

    def test_violation_is_error_severity(self) -> None:
        """CQS violations are error severity by default."""
        pattern = CQSPattern(
            function_name="mixed",
            line=1,
            column=0,
            file_path="test.py",
            inputs=[InputOperation(2, 4, "query()", "x")],
            outputs=[OutputOperation(3, 4, "command()")],
        )
        violation = build_cqs_violation(pattern)
        assert violation.severity.value == "error"


class TestViolationRuleId:
    """Tests for violation rule ID."""

    def test_violation_has_cqs_rule_id(self) -> None:
        """Violation has CQS rule ID."""
        pattern = CQSPattern(
            function_name="mixed",
            line=1,
            column=0,
            file_path="test.py",
            inputs=[InputOperation(2, 4, "query()", "x")],
            outputs=[OutputOperation(3, 4, "command()")],
        )
        violation = build_cqs_violation(pattern)
        assert "cqs" in violation.rule_id.lower()

    def test_violation_rule_id_format(self) -> None:
        """Violation rule ID follows project format."""
        pattern = CQSPattern(
            function_name="mixed",
            line=1,
            column=0,
            file_path="test.py",
            inputs=[InputOperation(2, 4, "query()", "x")],
            outputs=[OutputOperation(3, 4, "command()")],
        )
        violation = build_cqs_violation(pattern)
        assert violation.rule_id == "cqs"

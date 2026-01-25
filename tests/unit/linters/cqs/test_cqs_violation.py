"""
Purpose: Tests for CQS violation detection

Scope: Unit tests for identifying functions that mix INPUT and OUTPUT operations

Overview: Test suite for CQS violation detection. Tests identification of functions
    that violate Command-Query Separation by mixing queries (INPUTs) with commands
    (OUTPUTs). Covers simple violations, methods, async functions, nested functions,
    and complex multi-operation violations. Also tests valid patterns that should NOT
    be flagged.

Dependencies: pytest, src.linters.cqs

Exports: Test classes for violation detection

Interfaces: pytest test discovery and execution

Implementation: Tests using PythonCQSAnalyzer for violation detection
"""

from src.linters.cqs import (
    CQSConfig,
    CQSPattern,
    InputOperation,
    OutputOperation,
    PythonCQSAnalyzer,
)
from tests.unit.linters.cqs.conftest import (
    CQS_VALID_COMMAND_ONLY,
    CQS_VALID_QUERY_ONLY,
    CQS_VIOLATION_ASYNC,
    CQS_VIOLATION_BASIC,
    CQS_VIOLATION_METHOD,
    CQS_VIOLATION_MULTIPLE_INPUTS_OUTPUTS,
    CQS_VIOLATION_NESTED,
)


class TestBasicViolation:
    """Tests for basic CQS violation detection."""

    def test_detects_basic_violation(self) -> None:
        """Detects function with both INPUT and OUTPUT."""
        code = CQS_VIOLATION_BASIC
        analyzer = PythonCQSAnalyzer()
        patterns = analyzer.analyze(code, "test.py", CQSConfig())
        violations = [p for p in patterns if p.has_violation()]
        assert len(violations) == 1
        assert violations[0].function_name == "process_and_save"

    def test_violation_has_inputs(self) -> None:
        """Violation includes INPUT operations."""
        code = CQS_VIOLATION_BASIC
        analyzer = PythonCQSAnalyzer()
        patterns = analyzer.analyze(code, "test.py", CQSConfig())
        violation = [p for p in patterns if p.has_violation()][0]
        assert len(violation.inputs) >= 1

    def test_violation_has_outputs(self) -> None:
        """Violation includes OUTPUT operations."""
        code = CQS_VIOLATION_BASIC
        analyzer = PythonCQSAnalyzer()
        patterns = analyzer.analyze(code, "test.py", CQSConfig())
        violation = [p for p in patterns if p.has_violation()][0]
        assert len(violation.outputs) >= 1


class TestMultipleOperations:
    """Tests for violations with multiple INPUTs and OUTPUTs."""

    def test_detects_multiple_inputs_outputs(self) -> None:
        """Detects function with multiple INPUTs and multiple OUTPUTs."""
        code = CQS_VIOLATION_MULTIPLE_INPUTS_OUTPUTS
        analyzer = PythonCQSAnalyzer()
        patterns = analyzer.analyze(code, "test.py", CQSConfig())
        violations = [p for p in patterns if p.has_violation()]
        assert len(violations) == 1
        assert len(violations[0].inputs) >= 2
        assert len(violations[0].outputs) >= 2


class TestAsyncViolation:
    """Tests for async function CQS violations."""

    def test_detects_async_violation(self) -> None:
        """Detects async function with both INPUT and OUTPUT."""
        code = CQS_VIOLATION_ASYNC
        analyzer = PythonCQSAnalyzer()
        patterns = analyzer.analyze(code, "test.py", CQSConfig())
        violations = [p for p in patterns if p.has_violation()]
        assert len(violations) == 1
        assert violations[0].is_async is True


class TestMethodViolation:
    """Tests for class method CQS violations."""

    def test_detects_method_violation(self) -> None:
        """Detects class method with both INPUT and OUTPUT."""
        code = CQS_VIOLATION_METHOD
        analyzer = PythonCQSAnalyzer()
        patterns = analyzer.analyze(code, "test.py", CQSConfig())
        violations = [p for p in patterns if p.has_violation()]
        assert len(violations) == 1
        assert violations[0].is_method is True

    def test_method_has_class_name(self) -> None:
        """Method violation includes class name."""
        code = CQS_VIOLATION_METHOD
        analyzer = PythonCQSAnalyzer()
        patterns = analyzer.analyze(code, "test.py", CQSConfig())
        violation = [p for p in patterns if p.has_violation()][0]
        assert violation.class_name == "DataProcessor"

    def test_method_full_name(self) -> None:
        """Method get_full_name() returns ClassName.method."""
        code = CQS_VIOLATION_METHOD
        analyzer = PythonCQSAnalyzer()
        patterns = analyzer.analyze(code, "test.py", CQSConfig())
        violation = [p for p in patterns if p.has_violation()][0]
        assert violation.get_full_name() == "DataProcessor.process"


class TestNestedViolation:
    """Tests for nested function CQS violations."""

    def test_detects_nested_violation(self) -> None:
        """Detects violation in nested function."""
        code = CQS_VIOLATION_NESTED
        analyzer = PythonCQSAnalyzer()
        patterns = analyzer.analyze(code, "test.py", CQSConfig())
        violations = [p for p in patterns if p.has_violation()]
        assert len(violations) >= 1
        nested_violation = [v for v in violations if v.function_name == "inner"]
        assert len(nested_violation) == 1


class TestValidQueryOnly:
    """Tests for query-only functions (no violation)."""

    def test_query_only_not_violation(self) -> None:
        """Function with only INPUTs (queries) is not a violation."""
        code = CQS_VALID_QUERY_ONLY
        analyzer = PythonCQSAnalyzer()
        patterns = analyzer.analyze(code, "test.py", CQSConfig())
        violations = [p for p in patterns if p.has_violation()]
        assert len(violations) == 0

    def test_query_only_has_inputs(self) -> None:
        """Query-only function has INPUTs but no OUTPUTs."""
        code = CQS_VALID_QUERY_ONLY
        analyzer = PythonCQSAnalyzer()
        patterns = analyzer.analyze(code, "test.py", CQSConfig())
        query_fn = [p for p in patterns if p.function_name == "get_user_data"][0]
        assert len(query_fn.inputs) >= 1
        assert len(query_fn.outputs) == 0


class TestValidCommandOnly:
    """Tests for command-only functions (no violation)."""

    def test_command_only_not_violation(self) -> None:
        """Function with only OUTPUTs (commands) is not a violation."""
        code = CQS_VALID_COMMAND_ONLY
        analyzer = PythonCQSAnalyzer()
        patterns = analyzer.analyze(code, "test.py", CQSConfig())
        violations = [p for p in patterns if p.has_violation()]
        assert len(violations) == 0

    def test_command_only_has_outputs(self) -> None:
        """Command-only function has OUTPUTs but no INPUTs."""
        code = CQS_VALID_COMMAND_ONLY
        analyzer = PythonCQSAnalyzer()
        patterns = analyzer.analyze(code, "test.py", CQSConfig())
        cmd_fn = [p for p in patterns if p.function_name == "update_all_records"][0]
        assert len(cmd_fn.outputs) >= 1
        assert len(cmd_fn.inputs) == 0


class TestCQSPatternMethods:
    """Tests for CQSPattern dataclass methods."""

    def test_has_violation_true_when_mixed(self) -> None:
        """has_violation() returns True when both INPUTs and OUTPUTs exist."""
        pattern = CQSPattern(
            function_name="mixed",
            line=1,
            column=0,
            file_path="test.py",
            inputs=[InputOperation(1, 0, "query()", "x")],
            outputs=[OutputOperation(2, 0, "command()")],
        )
        assert pattern.has_violation() is True

    def test_has_violation_false_inputs_only(self) -> None:
        """has_violation() returns False for inputs-only."""
        pattern = CQSPattern(
            function_name="query",
            line=1,
            column=0,
            file_path="test.py",
            inputs=[InputOperation(1, 0, "query()", "x")],
            outputs=[],
        )
        assert pattern.has_violation() is False

    def test_has_violation_false_outputs_only(self) -> None:
        """has_violation() returns False for outputs-only."""
        pattern = CQSPattern(
            function_name="command",
            line=1,
            column=0,
            file_path="test.py",
            inputs=[],
            outputs=[OutputOperation(1, 0, "command()")],
        )
        assert pattern.has_violation() is False

    def test_has_violation_false_empty(self) -> None:
        """has_violation() returns False for empty function."""
        pattern = CQSPattern(
            function_name="empty",
            line=1,
            column=0,
            file_path="test.py",
            inputs=[],
            outputs=[],
        )
        assert pattern.has_violation() is False

    def test_get_full_name_function(self) -> None:
        """get_full_name() returns function name for non-method."""
        pattern = CQSPattern(
            function_name="process",
            line=1,
            column=0,
            file_path="test.py",
        )
        assert pattern.get_full_name() == "process"

    def test_get_full_name_method(self) -> None:
        """get_full_name() returns ClassName.method for method."""
        pattern = CQSPattern(
            function_name="process",
            line=1,
            column=0,
            file_path="test.py",
            is_method=True,
            class_name="DataProcessor",
        )
        assert pattern.get_full_name() == "DataProcessor.process"

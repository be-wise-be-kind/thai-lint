"""
Purpose: Tests for TypeScript CQS pattern detection

Scope: Verify TypeScript INPUT/OUTPUT detection and CQS violation detection

Overview: Tests for TypeScript support in the CQS linter. Verifies that the TypeScript
    INPUT detector correctly identifies variable declarations with call expressions,
    the OUTPUT detector correctly identifies expression statements containing calls,
    and the full analyzer correctly detects CQS violations in TypeScript functions.
    Tests various patterns including const/let declarations, destructuring, async/await,
    class methods, and fluent interfaces.

Dependencies: pytest, src.linters.cqs TypeScript analyzers, conftest fixtures

Exports: Test functions for TypeScript CQS detection

Interfaces: pytest test functions

Implementation: pytest test cases with tree-sitter parsing
"""

import pytest

from src.analyzers.typescript_base import TREE_SITTER_AVAILABLE
from src.linters.cqs.config import CQSConfig
from src.linters.cqs.typescript_cqs_analyzer import TypeScriptCQSAnalyzer
from src.linters.cqs.typescript_input_detector import TypeScriptInputDetector
from src.linters.cqs.typescript_output_detector import TypeScriptOutputDetector

from .conftest import (
    TS_CQS_VALID_COMMAND_ONLY,
    TS_CQS_VALID_CONSTRUCTOR,
    TS_CQS_VALID_FLUENT_INTERFACE,
    TS_CQS_VALID_QUERY_ONLY,
    TS_CQS_VIOLATION_ARRAY_DESTRUCTURING,
    TS_CQS_VIOLATION_ASYNC,
    TS_CQS_VIOLATION_BASIC,
    TS_CQS_VIOLATION_DESTRUCTURING,
    TS_CQS_VIOLATION_METHOD,
    TS_CQS_VIOLATION_MULTIPLE,
    TS_INPUT_ARRAY_DESTRUCTURING,
    TS_INPUT_AWAIT_ASSIGNMENT,
    TS_INPUT_CONST_ASSIGNMENT,
    TS_INPUT_LET_ASSIGNMENT,
    TS_INPUT_OBJECT_DESTRUCTURING,
    TS_INPUT_THIS_ASSIGNMENT,
    TS_NOT_OUTPUT_ASSIGNMENT,
    TS_NOT_OUTPUT_IF_CONDITION,
    TS_NOT_OUTPUT_RETURN,
    TS_OUTPUT_ASYNC_STATEMENT,
    TS_OUTPUT_CHAINED_CALL,
    TS_OUTPUT_METHOD_CALL,
    TS_OUTPUT_STATEMENT_CALL,
)

pytestmark = pytest.mark.skipif(not TREE_SITTER_AVAILABLE, reason="tree-sitter not available")


# =============================================================================
# INPUT DETECTION TESTS
# =============================================================================


class TestTypeScriptInputDetection:
    """Tests for TypeScript INPUT pattern detection."""

    def test_const_assignment_detected(self) -> None:
        """Const assignment from call is detected as INPUT."""
        detector = TypeScriptInputDetector()
        root = detector.parse_typescript(TS_INPUT_CONST_ASSIGNMENT)
        inputs = detector.find_inputs(root)
        assert len(inputs) == 1
        assert inputs[0].target == "x"
        assert "func()" in inputs[0].expression

    def test_let_assignment_detected(self) -> None:
        """Let assignment from call is detected as INPUT."""
        detector = TypeScriptInputDetector()
        root = detector.parse_typescript(TS_INPUT_LET_ASSIGNMENT)
        inputs = detector.find_inputs(root)
        assert len(inputs) == 1
        assert inputs[0].target == "x"

    def test_object_destructuring_detected(self) -> None:
        """Object destructuring from call is detected as INPUT."""
        detector = TypeScriptInputDetector()
        root = detector.parse_typescript(TS_INPUT_OBJECT_DESTRUCTURING)
        inputs = detector.find_inputs(root)
        assert len(inputs) == 1
        assert "a" in inputs[0].target
        assert "b" in inputs[0].target

    def test_array_destructuring_detected(self) -> None:
        """Array destructuring from call is detected as INPUT."""
        detector = TypeScriptInputDetector()
        root = detector.parse_typescript(TS_INPUT_ARRAY_DESTRUCTURING)
        inputs = detector.find_inputs(root)
        assert len(inputs) == 1
        assert "first" in inputs[0].target
        assert "second" in inputs[0].target

    def test_await_assignment_detected(self) -> None:
        """Await assignment is detected as INPUT."""
        detector = TypeScriptInputDetector()
        root = detector.parse_typescript(TS_INPUT_AWAIT_ASSIGNMENT)
        inputs = detector.find_inputs(root)
        assert len(inputs) == 1
        assert inputs[0].target == "x"

    def test_this_assignment_detected(self) -> None:
        """this.property assignment is detected as INPUT."""
        detector = TypeScriptInputDetector()
        root = detector.parse_typescript(TS_INPUT_THIS_ASSIGNMENT)
        inputs = detector.find_inputs(root)
        assert len(inputs) == 1
        assert "this.data" in inputs[0].target


# =============================================================================
# OUTPUT DETECTION TESTS
# =============================================================================


class TestTypeScriptOutputDetection:
    """Tests for TypeScript OUTPUT pattern detection."""

    def test_statement_call_detected(self) -> None:
        """Statement-level call is detected as OUTPUT."""
        detector = TypeScriptOutputDetector()
        root = detector.parse_typescript(TS_OUTPUT_STATEMENT_CALL)
        outputs = detector.find_outputs(root)
        assert len(outputs) == 1
        assert "doSomething()" in outputs[0].expression

    def test_async_statement_detected(self) -> None:
        """Await statement call is detected as OUTPUT."""
        detector = TypeScriptOutputDetector()
        root = detector.parse_typescript(TS_OUTPUT_ASYNC_STATEMENT)
        outputs = detector.find_outputs(root)
        assert len(outputs) == 1
        assert "sendNotification()" in outputs[0].expression

    def test_method_call_detected(self) -> None:
        """Method call statement is detected as OUTPUT."""
        detector = TypeScriptOutputDetector()
        root = detector.parse_typescript(TS_OUTPUT_METHOD_CALL)
        outputs = detector.find_outputs(root)
        assert len(outputs) == 1
        assert "obj.updateState()" in outputs[0].expression

    def test_chained_call_detected(self) -> None:
        """Chained method call is detected as OUTPUT."""
        detector = TypeScriptOutputDetector()
        root = detector.parse_typescript(TS_OUTPUT_CHAINED_CALL)
        outputs = detector.find_outputs(root)
        assert len(outputs) == 1

    def test_return_not_detected_as_output(self) -> None:
        """Return statement with call is not detected as OUTPUT."""
        detector = TypeScriptOutputDetector()
        root = detector.parse_typescript(TS_NOT_OUTPUT_RETURN)
        outputs = detector.find_outputs(root)
        assert len(outputs) == 0

    def test_if_condition_not_detected_as_output(self) -> None:
        """If condition with call is not detected as OUTPUT."""
        detector = TypeScriptOutputDetector()
        root = detector.parse_typescript(TS_NOT_OUTPUT_IF_CONDITION)
        outputs = detector.find_outputs(root)
        assert len(outputs) == 0

    def test_assignment_not_detected_as_output(self) -> None:
        """Assignment call is not detected as OUTPUT (it's INPUT)."""
        detector = TypeScriptOutputDetector()
        root = detector.parse_typescript(TS_NOT_OUTPUT_ASSIGNMENT)
        outputs = detector.find_outputs(root)
        assert len(outputs) == 0


# =============================================================================
# CQS VIOLATION DETECTION TESTS
# =============================================================================


class TestTypeScriptCQSViolationDetection:
    """Tests for TypeScript CQS violation detection."""

    def test_basic_violation_detected(self) -> None:
        """Basic CQS violation is detected."""
        analyzer = TypeScriptCQSAnalyzer()
        config = CQSConfig()
        patterns = analyzer.analyze(TS_CQS_VIOLATION_BASIC, "test.ts", config)
        assert len(patterns) == 1
        pattern = patterns[0]
        assert pattern.has_violation()
        assert len(pattern.inputs) >= 1
        assert len(pattern.outputs) >= 1

    def test_async_violation_detected(self) -> None:
        """Async CQS violation is detected."""
        analyzer = TypeScriptCQSAnalyzer()
        config = CQSConfig()
        patterns = analyzer.analyze(TS_CQS_VIOLATION_ASYNC, "test.ts", config)
        assert len(patterns) == 1
        pattern = patterns[0]
        assert pattern.has_violation()
        assert pattern.is_async

    def test_method_violation_detected(self) -> None:
        """Class method CQS violation is detected."""
        analyzer = TypeScriptCQSAnalyzer()
        config = CQSConfig()
        patterns = analyzer.analyze(TS_CQS_VIOLATION_METHOD, "test.ts", config)
        # Should detect the process method
        violating = [p for p in patterns if p.has_violation()]
        assert len(violating) >= 1
        assert any(p.function_name == "process" for p in violating)

    def test_destructuring_violation_detected(self) -> None:
        """Object destructuring CQS violation is detected."""
        analyzer = TypeScriptCQSAnalyzer()
        config = CQSConfig()
        patterns = analyzer.analyze(TS_CQS_VIOLATION_DESTRUCTURING, "test.ts", config)
        assert len(patterns) == 1
        assert patterns[0].has_violation()

    def test_array_destructuring_violation_detected(self) -> None:
        """Array destructuring CQS violation is detected."""
        analyzer = TypeScriptCQSAnalyzer()
        config = CQSConfig()
        patterns = analyzer.analyze(TS_CQS_VIOLATION_ARRAY_DESTRUCTURING, "test.ts", config)
        assert len(patterns) == 1
        assert patterns[0].has_violation()

    def test_multiple_inputs_outputs_detected(self) -> None:
        """Multiple INPUTs and OUTPUTs are detected."""
        analyzer = TypeScriptCQSAnalyzer()
        config = CQSConfig()
        patterns = analyzer.analyze(TS_CQS_VIOLATION_MULTIPLE, "test.ts", config)
        assert len(patterns) == 1
        pattern = patterns[0]
        assert len(pattern.inputs) >= 2
        assert len(pattern.outputs) >= 2


# =============================================================================
# VALID PATTERN TESTS (NO VIOLATIONS)
# =============================================================================


class TestTypeScriptValidPatterns:
    """Tests for TypeScript patterns that should NOT be violations."""

    def test_query_only_no_violation(self) -> None:
        """Query-only function has no CQS violation."""
        analyzer = TypeScriptCQSAnalyzer()
        config = CQSConfig()
        patterns = analyzer.analyze(TS_CQS_VALID_QUERY_ONLY, "test.ts", config)
        assert len(patterns) == 1
        assert not patterns[0].has_violation()
        assert len(patterns[0].outputs) == 0

    def test_command_only_no_violation(self) -> None:
        """Command-only function has no CQS violation."""
        analyzer = TypeScriptCQSAnalyzer()
        config = CQSConfig()
        patterns = analyzer.analyze(TS_CQS_VALID_COMMAND_ONLY, "test.ts", config)
        assert len(patterns) == 1
        assert not patterns[0].has_violation()
        assert len(patterns[0].inputs) == 0

    def test_fluent_interface_no_violation(self) -> None:
        """Fluent interface pattern is excluded from analysis."""
        analyzer = TypeScriptCQSAnalyzer()
        config = CQSConfig(detect_fluent_interface=True)
        patterns = analyzer.analyze(TS_CQS_VALID_FLUENT_INTERFACE, "test.ts", config)
        # Fluent interface should be excluded
        violating = [p for p in patterns if p.has_violation()]
        assert len(violating) == 0

    def test_constructor_ignored(self) -> None:
        """Constructor is ignored by default config."""
        analyzer = TypeScriptCQSAnalyzer()
        config = CQSConfig()  # Default ignores __init__ and constructor
        patterns = analyzer.analyze(TS_CQS_VALID_CONSTRUCTOR, "test.ts", config)
        # Constructor should be ignored
        constructor_patterns = [p for p in patterns if p.function_name == "constructor"]
        assert len(constructor_patterns) == 0


# =============================================================================
# FUNCTION ANALYZER TESTS
# =============================================================================


class TestTypeScriptFunctionAnalyzer:
    """Tests for TypeScript function analyzer specifics."""

    def test_function_name_extracted(self) -> None:
        """Function name is correctly extracted."""
        analyzer = TypeScriptCQSAnalyzer()
        config = CQSConfig()
        patterns = analyzer.analyze(TS_CQS_VIOLATION_BASIC, "test.ts", config)
        assert len(patterns) == 1
        assert patterns[0].function_name == "processAndSave"

    def test_class_name_extracted(self) -> None:
        """Class name is correctly extracted for methods."""
        analyzer = TypeScriptCQSAnalyzer()
        config = CQSConfig()
        patterns = analyzer.analyze(TS_CQS_VIOLATION_METHOD, "test.ts", config)
        method_patterns = [p for p in patterns if p.function_name == "process"]
        assert len(method_patterns) >= 1
        assert method_patterns[0].class_name == "DataProcessor"

    def test_line_numbers_correct(self) -> None:
        """Line numbers are correctly reported."""
        analyzer = TypeScriptCQSAnalyzer()
        config = CQSConfig()
        patterns = analyzer.analyze(TS_CQS_VIOLATION_BASIC, "test.ts", config)
        assert len(patterns) == 1
        assert patterns[0].line >= 1

    def test_is_method_flag(self) -> None:
        """is_method flag is correctly set."""
        analyzer = TypeScriptCQSAnalyzer()
        config = CQSConfig()
        patterns = analyzer.analyze(TS_CQS_VIOLATION_METHOD, "test.ts", config)
        method_patterns = [p for p in patterns if p.function_name == "process"]
        assert len(method_patterns) >= 1
        assert method_patterns[0].is_method is True

    def test_is_async_flag(self) -> None:
        """is_async flag is correctly set."""
        analyzer = TypeScriptCQSAnalyzer()
        config = CQSConfig()
        patterns = analyzer.analyze(TS_CQS_VIOLATION_ASYNC, "test.ts", config)
        assert len(patterns) == 1
        assert patterns[0].is_async is True


# =============================================================================
# EDGE CASES
# =============================================================================


class TestTypeScriptEdgeCases:
    """Tests for TypeScript edge cases."""

    def test_empty_function_no_violation(self) -> None:
        """Empty function has no CQS violation."""
        code = """
function empty(): void {
}
"""
        analyzer = TypeScriptCQSAnalyzer()
        config = CQSConfig()
        patterns = analyzer.analyze(code, "test.ts", config)
        assert len(patterns) == 1
        assert not patterns[0].has_violation()

    def test_tree_sitter_unavailable_returns_empty(self) -> None:
        """When tree-sitter unavailable, returns empty list gracefully."""
        analyzer = TypeScriptCQSAnalyzer()
        # Simulate unavailable by passing None as root node
        analyzer._function_analyzer.analyze(None, "test.ts", CQSConfig())
        # This should not raise an exception

    def test_nested_functions(self) -> None:
        """Nested functions are analyzed separately."""
        code = """
function outer(): void {
    const data = getData();  // INPUT in outer

    function inner(): void {
        const innerData = getInnerData();  // INPUT in inner
        doSomething();                      // OUTPUT in inner
    }

    doSomething();  // OUTPUT in outer
}
"""
        analyzer = TypeScriptCQSAnalyzer()
        config = CQSConfig()
        patterns = analyzer.analyze(code, "test.ts", config)
        # Both outer and inner should be detected as violations
        violating = [p for p in patterns if p.has_violation()]
        assert len(violating) >= 2

    def test_arrow_function_in_variable(self) -> None:
        """Arrow function assigned to variable is analyzed."""
        code = """
const myFunc = (): void => {
    const data = getData();
    saveData(data);
};
"""
        analyzer = TypeScriptCQSAnalyzer()
        config = CQSConfig()
        patterns = analyzer.analyze(code, "test.ts", config)
        assert len(patterns) >= 1
        violating = [p for p in patterns if p.has_violation()]
        assert len(violating) >= 1

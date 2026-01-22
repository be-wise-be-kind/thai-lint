"""
Purpose: Tests for INPUT operation detection in CQS linter

Scope: Unit tests for detecting query-like operations that capture return values

Overview: Test suite for INPUT operation detection. Tests identification of
    assignment patterns where function call results are captured: simple assignments
    (x = func()), tuple unpacking (x, y = func()), async assignments (x = await func()),
    attribute assignments (self.x = func()), subscript assignments (x[key] = func()),
    and walrus operator (:=). Validates that non-call assignments are excluded.

Dependencies: pytest, ast, src.linters.cqs

Exports: Test classes for INPUT detection

Interfaces: pytest test discovery and execution

Implementation: pytest test classes with fixture-based test data
"""

import ast

from src.linters.cqs import InputDetector
from tests.unit.linters.cqs.conftest import (
    INPUT_ANNOTATED_ASSIGNMENT,
    INPUT_ASYNC_ASSIGNMENT,
    INPUT_ATTRIBUTE_ASSIGNMENT,
    INPUT_SIMPLE_ASSIGNMENT,
    INPUT_SUBSCRIPT_ASSIGNMENT,
    INPUT_TUPLE_UNPACKING,
    INPUT_WALRUS_OPERATOR,
)


class TestSimpleAssignment:
    """Tests for simple assignment INPUT patterns."""

    def test_detects_simple_assignment(self) -> None:
        """Detects x = func() as INPUT."""
        code = INPUT_SIMPLE_ASSIGNMENT
        detector = InputDetector()
        inputs = detector.find_inputs(ast.parse(code))
        assert len(inputs) == 1
        assert inputs[0].target == "x"
        assert inputs[0].expression == "func()"

    def test_captures_line_and_column(self) -> None:
        """INPUT includes line and column information."""
        code = INPUT_SIMPLE_ASSIGNMENT
        detector = InputDetector()
        inputs = detector.find_inputs(ast.parse(code))
        assert inputs[0].line == 3
        assert inputs[0].column >= 0

    def test_detects_chained_call_assignment(self) -> None:
        """Detects x = obj.method() as INPUT."""
        code = "def f():\n    x = obj.method()"
        detector = InputDetector()
        inputs = detector.find_inputs(ast.parse(code))
        assert len(inputs) == 1


class TestTupleUnpacking:
    """Tests for tuple unpacking INPUT patterns."""

    def test_detects_tuple_unpacking(self) -> None:
        """Detects x, y = func() as INPUT."""
        code = INPUT_TUPLE_UNPACKING
        detector = InputDetector()
        inputs = detector.find_inputs(ast.parse(code))
        assert len(inputs) == 1
        assert "x" in inputs[0].target and "y" in inputs[0].target

    def test_captures_all_targets(self) -> None:
        """Tuple unpacking captures all target names."""
        code = INPUT_TUPLE_UNPACKING
        detector = InputDetector()
        inputs = detector.find_inputs(ast.parse(code))
        assert inputs[0].target == "x, y"

    def test_triple_unpacking(self) -> None:
        """Detects a, b, c = func() as INPUT."""
        code = "def f():\n    a, b, c = get_triple()"
        detector = InputDetector()
        inputs = detector.find_inputs(ast.parse(code))
        assert len(inputs) == 1


class TestAsyncAssignment:
    """Tests for async assignment INPUT patterns."""

    def test_detects_async_assignment(self) -> None:
        """Detects x = await func() as INPUT."""
        code = INPUT_ASYNC_ASSIGNMENT
        detector = InputDetector()
        inputs = detector.find_inputs(ast.parse(code))
        assert len(inputs) == 1

    def test_async_method_call(self) -> None:
        """Detects x = await obj.method() as INPUT."""
        code = "async def f():\n    x = await self.fetch()"
        detector = InputDetector()
        inputs = detector.find_inputs(ast.parse(code))
        assert len(inputs) == 1


class TestAttributeAssignment:
    """Tests for attribute assignment INPUT patterns."""

    def test_detects_attribute_assignment(self) -> None:
        """Detects self.x = func() as INPUT."""
        code = INPUT_ATTRIBUTE_ASSIGNMENT
        detector = InputDetector()
        inputs = detector.find_inputs(ast.parse(code))
        assert len(inputs) == 1
        assert "self.data" in inputs[0].target

    def test_detects_nested_attribute(self) -> None:
        """Detects self.obj.attr = func() as INPUT."""
        code = "def f(self):\n    self.obj.attr = compute()"
        detector = InputDetector()
        inputs = detector.find_inputs(ast.parse(code))
        assert len(inputs) == 1


class TestSubscriptAssignment:
    """Tests for subscript assignment INPUT patterns."""

    def test_detects_subscript_assignment(self) -> None:
        """Detects x[key] = func() as INPUT."""
        code = INPUT_SUBSCRIPT_ASSIGNMENT
        detector = InputDetector()
        inputs = detector.find_inputs(ast.parse(code))
        assert len(inputs) == 1

    def test_detects_dict_subscript(self) -> None:
        """Detects dict[key] = func() as INPUT."""
        code = "def f():\n    cache['result'] = compute()"
        detector = InputDetector()
        inputs = detector.find_inputs(ast.parse(code))
        assert len(inputs) == 1


class TestAnnotatedAssignment:
    """Tests for annotated assignment INPUT patterns."""

    def test_detects_annotated_assignment(self) -> None:
        """Detects result: int = func() as INPUT."""
        code = INPUT_ANNOTATED_ASSIGNMENT
        detector = InputDetector()
        inputs = detector.find_inputs(ast.parse(code))
        assert len(inputs) == 1


class TestWalrusOperator:
    """Tests for walrus operator INPUT patterns."""

    def test_detects_walrus_in_if(self) -> None:
        """Detects if (x := func()) as INPUT."""
        code = INPUT_WALRUS_OPERATOR
        detector = InputDetector()
        inputs = detector.find_inputs(ast.parse(code))
        assert len(inputs) == 1

    def test_detects_walrus_in_while(self) -> None:
        """Detects while (x := func()) as INPUT."""
        code = "def f():\n    while (data := next_item()) is not None:\n        pass"
        detector = InputDetector()
        inputs = detector.find_inputs(ast.parse(code))
        assert len(inputs) == 1


class TestInputExclusions:
    """Tests for patterns that should NOT be detected as INPUT."""

    def test_literal_assignment_not_input(self) -> None:
        """x = 5 is not an INPUT (no function call)."""
        code = "def f():\n    x = 5"
        detector = InputDetector()
        inputs = detector.find_inputs(ast.parse(code))
        assert len(inputs) == 0

    def test_variable_assignment_not_input(self) -> None:
        """x = y is not an INPUT (no function call)."""
        code = "def f():\n    y = 1\n    x = y"
        detector = InputDetector()
        inputs = detector.find_inputs(ast.parse(code))
        assert len(inputs) == 0

    def test_expression_assignment_not_input(self) -> None:
        """x = a + b is not an INPUT (no function call)."""
        code = "def f():\n    x = a + b"
        detector = InputDetector()
        inputs = detector.find_inputs(ast.parse(code))
        assert len(inputs) == 0

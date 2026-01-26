"""
Purpose: Tests for OUTPUT operation detection in CQS linter

Scope: Unit tests for detecting command-like operations that discard return values

Overview: Test suite for OUTPUT operation detection. Tests identification of
    statement-level function calls where return values are not captured: statement
    calls (func()), async statements (await func()), method calls (obj.method()),
    and chained calls. Critically tests patterns that should NOT be detected as
    OUTPUT: return statements, conditionals, assignments, and comprehensions.

Dependencies: pytest, ast, src.linters.cqs

Exports: Test classes for OUTPUT detection

Interfaces: pytest test discovery and execution

Implementation: pytest test classes with fixture-based test data
"""

import ast

from src.linters.cqs import OutputDetector
from tests.unit.linters.cqs.conftest import (
    NOT_OUTPUT_ASSERT,
    NOT_OUTPUT_ASSIGNMENT,
    NOT_OUTPUT_COMPREHENSION,
    NOT_OUTPUT_IF_CONDITION,
    NOT_OUTPUT_RETURN,
    NOT_OUTPUT_WHILE_CONDITION,
    OUTPUT_ASYNC_STATEMENT,
    OUTPUT_CHAINED_CALL,
    OUTPUT_METHOD_CALL,
    OUTPUT_STATEMENT_CALL,
)


class TestStatementCall:
    """Tests for statement-level call OUTPUT patterns."""

    def test_detects_statement_call(self) -> None:
        """Detects func() as OUTPUT when standalone statement."""
        code = OUTPUT_STATEMENT_CALL
        detector = OutputDetector()
        outputs = detector.find_outputs(ast.parse(code))
        assert len(outputs) == 1
        assert "do_something()" in outputs[0].expression

    def test_captures_line_and_column(self) -> None:
        """OUTPUT includes line and column information."""
        code = OUTPUT_STATEMENT_CALL
        detector = OutputDetector()
        outputs = detector.find_outputs(ast.parse(code))
        assert outputs[0].line == 3
        assert outputs[0].column >= 0

    def test_detects_multiple_statements(self) -> None:
        """Detects multiple statement calls as separate OUTPUTs."""
        code = "def f():\n    first()\n    second()"
        detector = OutputDetector()
        outputs = detector.find_outputs(ast.parse(code))
        assert len(outputs) == 2


class TestAsyncStatement:
    """Tests for async statement OUTPUT patterns."""

    def test_detects_await_statement(self) -> None:
        """Detects await func() as OUTPUT when standalone statement."""
        code = OUTPUT_ASYNC_STATEMENT
        detector = OutputDetector()
        outputs = detector.find_outputs(ast.parse(code))
        assert len(outputs) == 1

    def test_detects_await_method_call(self) -> None:
        """Detects await obj.method() as OUTPUT."""
        code = "async def f():\n    await self.notify()"
        detector = OutputDetector()
        outputs = detector.find_outputs(ast.parse(code))
        assert len(outputs) == 1


class TestMethodCall:
    """Tests for method call OUTPUT patterns."""

    def test_detects_method_call(self) -> None:
        """Detects obj.method() as OUTPUT when standalone statement."""
        code = OUTPUT_METHOD_CALL
        detector = OutputDetector()
        outputs = detector.find_outputs(ast.parse(code))
        assert len(outputs) == 1

    def test_detects_self_method_call(self) -> None:
        """Detects self.method() as OUTPUT."""
        code = "def f(self):\n    self.update()"
        detector = OutputDetector()
        outputs = detector.find_outputs(ast.parse(code))
        assert len(outputs) == 1


class TestChainedCall:
    """Tests for chained call OUTPUT patterns."""

    def test_detects_chained_call(self) -> None:
        """Detects obj.method().method2() as OUTPUT when standalone."""
        code = OUTPUT_CHAINED_CALL
        detector = OutputDetector()
        outputs = detector.find_outputs(ast.parse(code))
        assert len(outputs) == 1


class TestNotOutputReturn:
    """Tests for return statement patterns (should NOT be OUTPUT)."""

    def test_return_call_not_output(self) -> None:
        """return func() is NOT an OUTPUT - return uses the value."""
        code = NOT_OUTPUT_RETURN
        detector = OutputDetector()
        outputs = detector.find_outputs(ast.parse(code))
        assert len(outputs) == 0

    def test_return_method_call_not_output(self) -> None:
        """return obj.method() is NOT an OUTPUT."""
        code = "def f() -> int:\n    return self.calculate()"
        detector = OutputDetector()
        outputs = detector.find_outputs(ast.parse(code))
        assert len(outputs) == 0

    def test_return_await_not_output(self) -> None:
        """return await func() is NOT an OUTPUT."""
        code = "async def f() -> int:\n    return await fetch()"
        detector = OutputDetector()
        outputs = detector.find_outputs(ast.parse(code))
        assert len(outputs) == 0


class TestNotOutputConditional:
    """Tests for conditional patterns (should NOT be OUTPUT)."""

    def test_if_condition_not_output(self) -> None:
        """if func(): is NOT an OUTPUT - conditional uses the value."""
        code = NOT_OUTPUT_IF_CONDITION
        detector = OutputDetector()
        outputs = detector.find_outputs(ast.parse(code))
        assert len(outputs) == 0

    def test_while_condition_not_output(self) -> None:
        """while func(): is NOT an OUTPUT - loop uses the value."""
        code = NOT_OUTPUT_WHILE_CONDITION
        detector = OutputDetector()
        outputs = detector.find_outputs(ast.parse(code))
        assert len(outputs) == 0

    def test_elif_condition_not_output(self) -> None:
        """elif func(): is NOT an OUTPUT."""
        code = "def f():\n    if x:\n        pass\n    elif check():\n        pass"
        detector = OutputDetector()
        outputs = detector.find_outputs(ast.parse(code))
        assert len(outputs) == 0

    def test_ternary_not_output(self) -> None:
        """x if func() else y is NOT an OUTPUT."""
        code = "def f():\n    result = a if check() else b"
        detector = OutputDetector()
        outputs = detector.find_outputs(ast.parse(code))
        assert len(outputs) == 0


class TestNotOutputAssignment:
    """Tests for assignment patterns (should NOT be OUTPUT)."""

    def test_assignment_not_output(self) -> None:
        """x = func() is NOT an OUTPUT - it's an INPUT."""
        code = NOT_OUTPUT_ASSIGNMENT
        detector = OutputDetector()
        outputs = detector.find_outputs(ast.parse(code))
        assert len(outputs) == 0

    def test_annotated_assignment_not_output(self) -> None:
        """x: int = func() is NOT an OUTPUT."""
        code = "def f():\n    x: int = compute()"
        detector = OutputDetector()
        outputs = detector.find_outputs(ast.parse(code))
        assert len(outputs) == 0


class TestNotOutputComprehension:
    """Tests for comprehension patterns (should NOT be OUTPUT)."""

    def test_list_comprehension_not_output(self) -> None:
        """[func(x) for x in items] is NOT an OUTPUT."""
        code = NOT_OUTPUT_COMPREHENSION
        detector = OutputDetector()
        outputs = detector.find_outputs(ast.parse(code))
        assert len(outputs) == 0

    def test_dict_comprehension_not_output(self) -> None:
        """{k: func(v) for k, v in items} is NOT an OUTPUT."""
        code = "def f():\n    return {k: process(v) for k, v in items}"
        detector = OutputDetector()
        outputs = detector.find_outputs(ast.parse(code))
        assert len(outputs) == 0


class TestNotOutputAssert:
    """Tests for assert patterns (should NOT be OUTPUT)."""

    def test_assert_not_output(self) -> None:
        """assert func() is NOT an OUTPUT - assert uses the value."""
        code = NOT_OUTPUT_ASSERT
        detector = OutputDetector()
        outputs = detector.find_outputs(ast.parse(code))
        assert len(outputs) == 0


class TestNotOutputOther:
    """Tests for other patterns that should NOT be OUTPUT."""

    def test_for_iter_not_output(self) -> None:
        """for x in func(): is NOT an OUTPUT."""
        code = "def f():\n    for item in get_items():\n        pass"
        detector = OutputDetector()
        outputs = detector.find_outputs(ast.parse(code))
        assert len(outputs) == 0

    def test_with_context_not_output(self) -> None:
        """with func() as x: is NOT an OUTPUT."""
        code = "def f():\n    with open_file() as f:\n        pass"
        detector = OutputDetector()
        outputs = detector.find_outputs(ast.parse(code))
        assert len(outputs) == 0

    def test_raise_not_output(self) -> None:
        """raise func() is NOT an OUTPUT."""
        code = "def f():\n    raise create_error()"
        detector = OutputDetector()
        outputs = detector.find_outputs(ast.parse(code))
        assert len(outputs) == 0

    def test_yield_not_output(self) -> None:
        """yield func() is NOT an OUTPUT."""
        code = "def f():\n    yield generate()"
        detector = OutputDetector()
        outputs = detector.find_outputs(ast.parse(code))
        assert len(outputs) == 0

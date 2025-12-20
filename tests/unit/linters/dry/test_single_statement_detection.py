"""
Purpose: Unit tests for single statement detection methods in SingleStatementDetector

Scope: Testing specialized detection methods for multi-line single logical statements

Overview: Comprehensive parameterized test suite for each detection method including decorator
    detection, function call detection, list literal detection, dict literal detection, and other
    patterns that represent single logical statements spanning multiple lines. Ensures accurate
    identification to prevent false positive duplication violations on formatted code patterns.
    Tests boundary conditions and various formatting styles for each pattern type.

Dependencies: pytest, src.linters.dry.single_statement_detector.SingleStatementDetector

Exports: TestIsPartOfDecorator, TestIsPartOfFunctionCall, TestIsPartOfListLiteral,
    TestIsPartOfDictLiteral test classes

Interfaces: test methods with parameterized inputs for code samples, start_line, end_line, expected result

Implementation: Uses pytest parametrization with concrete examples for each pattern, detector fixture
    provides SingleStatementDetector instance, validates detection logic for each method independently
"""

import pytest

from src.linters.dry.single_statement_detector import SingleStatementDetector


@pytest.fixture
def detector():
    """Create a SingleStatementDetector instance for testing."""
    return SingleStatementDetector()


class TestIsPartOfDecorator:
    """Test is_part_of_decorator method."""

    @pytest.mark.parametrize(
        "code,start_line,end_line,expected",
        [
            # Test 1: Decorator arguments (should be True)
            (
                """
import click

@click.option(
    "--format", "-f", type=click.Choice(["text", "json"]), default="text"
)
def command_one():
    return "one"
""",
                4,  # Line with "--format"
                6,  # Line with closing paren
                True,
            ),
            # Test 2: Just the decorator line itself
            (
                """
@click.option(
    "--format", "-f"
)
def foo():
    pass
""",
                2,  # Line with "--format"
                3,  # Line with closing paren
                True,
            ),
            # Test 3: Multiple decorators (part of single function)
            (
                """
@decorator1
@decorator2(
    arg="value"
)
def foo():
    pass
""",
                3,  # Line with arg="value"
                4,  # Line with closing paren
                True,
            ),
            # Test 4: NOT a decorator - just regular code
            (
                """
def foo():
    x = 1
    y = 2
    z = 3
""",
                3,  # x = 1
                5,  # z = 3
                False,
            ),
        ],
    )
    def test_decorator_detection(self, detector, code, start_line, end_line, expected):
        """Test decorator detection with various patterns."""
        lines = code.strip().split("\n")
        result = detector.is_part_of_decorator(lines, start_line, end_line)
        assert result == expected, f"Expected {expected} for lines {start_line}-{end_line}"


class TestIsPartOfFunctionCall:
    """Test is_part_of_function_call method."""

    @pytest.mark.parametrize(
        "code,start_line,end_line,expected",
        [
            # Test 1: Constructor arguments
            (
                """
block = CodeBlock(
    file_path=file_path,
    start_line=start,
    end_line=end,
)
""",
                3,  # start_line=start
                4,  # end_line=end
                True,
            ),
            # Test 2: Nested function call
            (
                """
result = outer(
    inner(
        arg1=1,
        arg2=2
    )
)
""",
                4,  # arg1=1
                5,  # arg2=2
                True,
            ),
            # Test 3: Complete assignment (standalone single statement)
            (
                """
x = some_function(
    arg1=1
)
""",
                1,  # Entire statement
                3,
                True,
            ),
            # Test 4: NOT a function call - separate statements
            (
                """
x = 1
y = 2
z = 3
""",
                1,
                3,
                False,
            ),
        ],
    )
    def test_function_call_detection(self, detector, code, start_line, end_line, expected):
        """Test function call detection with various patterns."""
        lines = code.strip().split("\n")
        result = detector.is_part_of_function_call(lines, start_line, end_line)
        assert result == expected, f"Expected {expected} for lines {start_line}-{end_line}"


class TestIsPartOfClassBody:
    """Test is_part_of_class_body method."""

    @pytest.mark.parametrize(
        "code,start_line,end_line,expected",
        [
            # Test 1: Dataclass fields
            (
                """
@dataclass
class CodeBlock:
    file_path: Path
    start_line: int
    end_line: int
    snippet: str
""",
                4,  # start_line: int
                6,  # snippet: str
                True,
            ),
            # Test 2: Regular class attributes
            (
                """
class Config:
    host: str
    port: int
    timeout: float
""",
                2,  # host: str
                4,  # timeout: float
                True,
            ),
            # Test 3: Class with methods (fields only)
            (
                """
class Foo:
    field1: int
    field2: str

    def method(self):
        pass
""",
                2,  # field1: int
                3,  # field2: str
                True,
            ),
            # Test 4: NOT a class body - function body
            (
                """
def foo():
    x: int = 1
    y: int = 2
""",
                2,
                3,
                False,
            ),
        ],
    )
    def test_class_body_detection(self, detector, code, start_line, end_line, expected):
        """Test class body detection with various patterns."""
        lines = code.strip().split("\n")
        result = detector.is_part_of_class_body(lines, start_line, end_line)
        assert result == expected, f"Expected {expected} for lines {start_line}-{end_line}"


class TestIsStandaloneSingleStatement:
    """Test is_standalone_single_statement method."""

    @pytest.mark.parametrize(
        "code,start_line,end_line,expected",
        [
            # Test 1: Single assignment
            (
                """
x = some_function(
    arg1=1
)
""",
                1,
                3,
                True,
            ),
            # Test 2: Single if statement
            (
                """
if condition:
    do_something()
""",
                1,
                2,
                True,
            ),
            # Test 3: Multiple statements
            (
                """
x = 1
y = 2
z = 3
""",
                1,
                3,
                False,
            ),
            # Test 4: Partial statement (doesn't parse)
            (
                """
    arg1=value1,
    arg2=value2,
""",
                1,
                2,
                False,
            ),
        ],
    )
    def test_standalone_single_statement(self, detector, code, start_line, end_line, expected):
        """Test standalone single statement detection."""
        lines = code.strip().split("\n")
        result = detector.is_standalone_single_statement(lines, start_line, end_line)
        assert result == expected, f"Expected {expected} for lines {start_line}-{end_line}"


class TestIntegration:
    """Integration tests using is_single_statement (the main entry point)."""

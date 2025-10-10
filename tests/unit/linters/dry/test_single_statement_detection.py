"""
Purpose: Unit tests for single statement detection methods in PythonDuplicateAnalyzer

Scope: Test each specialized detection method (_is_part_of_decorator, _is_part_of_function_call, etc.)

Overview: Provides comprehensive parameterized tests for each detection method to ensure
    they correctly identify single logical statements spanning multiple lines.

Dependencies: pytest, src.linters.dry.python_analyzer.PythonDuplicateAnalyzer

Exports: Test functions for each detection method

Implementation: Uses parameterized tests with concrete examples of each pattern
"""

import pytest

from src.linters.dry.python_analyzer import PythonDuplicateAnalyzer


@pytest.fixture
def analyzer():
    """Create a PythonDuplicateAnalyzer instance for testing."""
    return PythonDuplicateAnalyzer()


class TestIsPartOfDecorator:
    """Test _is_part_of_decorator method."""

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
    def test_decorator_detection(self, analyzer, code, start_line, end_line, expected):
        """Test decorator detection with various patterns."""
        lines = code.strip().split("\n")
        result = analyzer._is_part_of_decorator(lines, start_line, end_line)
        assert result == expected, f"Expected {expected} for lines {start_line}-{end_line}"


class TestIsPartOfFunctionCall:
    """Test _is_part_of_function_call method."""

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
    def test_function_call_detection(self, analyzer, code, start_line, end_line, expected):
        """Test function call detection with various patterns."""
        lines = code.strip().split("\n")
        result = analyzer._is_part_of_function_call(lines, start_line, end_line)
        assert result == expected, f"Expected {expected} for lines {start_line}-{end_line}"


class TestIsPartOfClassBody:
    """Test _is_part_of_class_body method."""

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
    def test_class_body_detection(self, analyzer, code, start_line, end_line, expected):
        """Test class body detection with various patterns."""
        lines = code.strip().split("\n")
        result = analyzer._is_part_of_class_body(lines, start_line, end_line)
        assert result == expected, f"Expected {expected} for lines {start_line}-{end_line}"


class TestIsStandaloneSingleStatement:
    """Test _is_standalone_single_statement method."""

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
    def test_standalone_single_statement(self, analyzer, code, start_line, end_line, expected):
        """Test standalone single statement detection."""
        lines = code.strip().split("\n")
        result = analyzer._is_standalone_single_statement(lines, start_line, end_line)
        assert result == expected, f"Expected {expected} for lines {start_line}-{end_line}"


class TestIntegration:
    """Integration tests using _is_single_statement_in_source (the main entry point)."""

    @pytest.mark.parametrize(
        "code,start_line,end_line,expected,description",
        [
            # Decorator case
            (
                """
import click

@click.option(
    "--format", "-f", type=click.Choice(["text", "json"]), default="text"
)
def command_one():
    return "one"
""",
                4,
                6,
                True,
                "Decorator arguments",
            ),
            # Constructor call case
            (
                """
block = CodeBlock(
    file_path=file_path,
    start_line=start,
    end_line=end,
)
""",
                3,
                4,
                True,
                "Constructor arguments",
            ),
            # Dataclass fields case
            (
                """
@dataclass
class CodeBlock:
    file_path: Path
    start_line: int
    end_line: int
""",
                4,
                5,
                True,
                "Dataclass fields",
            ),
            # Multiple separate statements (should NOT be filtered)
            (
                """
def process():
    x = validate(data)
    y = transform(x)
    z = save(y)
""",
                3,
                5,
                False,
                "Multiple separate statements",
            ),
        ],
    )
    @pytest.mark.skip(reason="100% duplicate")
    def test_integration(self, analyzer, code, start_line, end_line, expected, description):
        """Test the main _is_single_statement_in_source method."""
        result = analyzer._is_single_statement_in_source(code.strip(), start_line, end_line)
        assert result == expected, (
            f"{description}: Expected {expected} for lines {start_line}-{end_line}"
        )

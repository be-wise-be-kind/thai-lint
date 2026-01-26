"""
Purpose: Tests for CQS linter edge cases

Scope: Unit tests for edge cases, configuration ignores, and special patterns

Overview: Test suite for CQS linter edge cases. Tests constructor ignoring
    (__init__, __new__), property decorator exclusions, fluent interface detection
    (return self), empty functions, nested classes, lambda expressions, generators,
    and error handling for malformed code.

Dependencies: pytest, src.linters.cqs

Exports: Test classes for edge cases

Interfaces: pytest test discovery and execution

Implementation: Tests using PythonCQSAnalyzer with various configurations
"""

from src.linters.cqs import CQSConfig, PythonCQSAnalyzer
from tests.unit.linters.cqs.conftest import (
    CQS_VALID_CONSTRUCTOR,
    CQS_VALID_FLUENT_INTERFACE,
    CQS_VALID_PROPERTY,
    CQS_VIOLATION_BASIC,
    EDGE_CASE_EMPTY_FUNCTION,
    EDGE_CASE_GENERATOR,
    EDGE_CASE_LAMBDA,
    EDGE_CASE_NESTED_CLASS,
    EDGE_CASE_ONLY_DOCSTRING,
)


class TestConstructorIgnore:
    """Tests for constructor method ignoring."""

    def test_init_ignored_by_default(self) -> None:
        """__init__ methods are ignored by default."""
        code = CQS_VALID_CONSTRUCTOR
        analyzer = PythonCQSAnalyzer()
        patterns = analyzer.analyze(code, "test.py", CQSConfig())
        # __init__ should not be in patterns
        init_patterns = [p for p in patterns if p.function_name == "__init__"]
        assert len(init_patterns) == 0

    def test_new_ignored_by_default(self) -> None:
        """__new__ methods are ignored by default."""
        code = "class C:\n    def __new__(cls):\n        x = allocate()\n        register(x)\n        return x"
        analyzer = PythonCQSAnalyzer()
        config = CQSConfig()
        patterns = analyzer.analyze(code, "test.py", config)
        # __new__ should not be in patterns
        new_patterns = [p for p in patterns if p.function_name == "__new__"]
        assert len(new_patterns) == 0

    def test_constructor_detected_with_strict_config(self) -> None:
        """Constructor violations detected when ignore_methods is empty."""
        code = CQS_VALID_CONSTRUCTOR
        analyzer = PythonCQSAnalyzer()
        config = CQSConfig(ignore_methods=[])
        patterns = analyzer.analyze(code, "test.py", config)
        init_patterns = [p for p in patterns if p.function_name == "__init__"]
        assert len(init_patterns) >= 1
        # Check if it's detected as a violation
        init_violations = [p for p in init_patterns if p.has_violation()]
        assert len(init_violations) >= 1


class TestDecoratorIgnore:
    """Tests for decorator-based ignoring."""

    def test_property_ignored_by_default(self) -> None:
        """@property methods are ignored by default."""
        code = CQS_VALID_PROPERTY
        analyzer = PythonCQSAnalyzer()
        patterns = analyzer.analyze(code, "test.py", CQSConfig())
        # Should have no violations (property is ignored)
        violations = [p for p in patterns if p.has_violation()]
        assert len(violations) == 0

    def test_cached_property_ignored_by_default(self) -> None:
        """@cached_property methods are ignored by default."""
        code = "class C:\n    @cached_property\n    def data(self):\n        x = load()\n        save(x)\n        return x"
        analyzer = PythonCQSAnalyzer()
        patterns = analyzer.analyze(code, "test.py", CQSConfig())
        violations = [p for p in patterns if p.has_violation()]
        assert len(violations) == 0

    def test_custom_decorator_ignored(self) -> None:
        """Custom decorator can be added to ignore list."""
        code = "class C:\n    @my_decorator\n    def mixed(self):\n        x = query()\n        command(x)"
        analyzer = PythonCQSAnalyzer()
        config = CQSConfig(ignore_decorators=["property", "cached_property", "my_decorator"])
        patterns = analyzer.analyze(code, "test.py", config)
        violations = [p for p in patterns if p.has_violation()]
        assert len(violations) == 0

    def test_staticmethod_not_ignored_by_default(self) -> None:
        """@staticmethod is NOT ignored by default."""
        code = (
            "class C:\n    @staticmethod\n    def mixed():\n        x = query()\n        command(x)"
        )
        analyzer = PythonCQSAnalyzer()
        patterns = analyzer.analyze(code, "test.py", CQSConfig())
        violations = [p for p in patterns if p.has_violation()]
        assert len(violations) >= 1


class TestFluentInterface:
    """Tests for fluent interface detection."""

    def test_fluent_interface_not_violation(self) -> None:
        """return self pattern is not flagged as violation."""
        code = CQS_VALID_FLUENT_INTERFACE
        analyzer = PythonCQSAnalyzer()
        config = CQSConfig(detect_fluent_interface=True)
        patterns = analyzer.analyze(code, "test.py", config)
        # Fluent interface should be excluded
        violations = [p for p in patterns if p.has_violation()]
        assert len(violations) == 0

    def test_fluent_interface_flagged_when_disabled(self) -> None:
        """return self is analyzed when detect_fluent_interface is False."""
        code = CQS_VALID_FLUENT_INTERFACE
        analyzer = PythonCQSAnalyzer()
        config = CQSConfig(detect_fluent_interface=False)
        patterns = analyzer.analyze(code, "test.py", config)
        # When fluent detection disabled, function is analyzed
        assert len(patterns) >= 1


class TestEmptyFunction:
    """Tests for empty functions."""

    def test_empty_function_no_violation(self) -> None:
        """Empty function (pass only) is not a violation."""
        code = EDGE_CASE_EMPTY_FUNCTION
        analyzer = PythonCQSAnalyzer()
        patterns = analyzer.analyze(code, "test.py", CQSConfig())
        violations = [p for p in patterns if p.has_violation()]
        assert len(violations) == 0

    def test_docstring_only_no_violation(self) -> None:
        """Function with only docstring is not a violation."""
        code = EDGE_CASE_ONLY_DOCSTRING
        analyzer = PythonCQSAnalyzer()
        patterns = analyzer.analyze(code, "test.py", CQSConfig())
        violations = [p for p in patterns if p.has_violation()]
        assert len(violations) == 0


class TestNestedClass:
    """Tests for nested class handling."""

    def test_nested_class_method_detected(self) -> None:
        """Violation in nested class method is detected."""
        code = EDGE_CASE_NESTED_CLASS
        analyzer = PythonCQSAnalyzer()
        patterns = analyzer.analyze(code, "test.py", CQSConfig())
        violations = [p for p in patterns if p.has_violation()]
        assert len(violations) >= 1

    def test_nested_class_name_correct(self) -> None:
        """Nested class name is correctly captured."""
        code = EDGE_CASE_NESTED_CLASS
        analyzer = PythonCQSAnalyzer()
        patterns = analyzer.analyze(code, "test.py", CQSConfig())
        violations = [p for p in patterns if p.has_violation()]
        # class_name should be "Inner" (the immediate class)
        assert any(v.class_name == "Inner" for v in violations)


class TestLambda:
    """Tests for lambda expression handling."""

    def test_lambda_not_analyzed(self) -> None:
        """Lambda expressions are not analyzed for CQS."""
        code = EDGE_CASE_LAMBDA
        analyzer = PythonCQSAnalyzer()
        patterns = analyzer.analyze(code, "test.py", CQSConfig())
        lambda_patterns = [p for p in patterns if "lambda" in p.function_name.lower()]
        assert len(lambda_patterns) == 0


class TestGenerator:
    """Tests for generator function handling."""

    def test_generator_analyzed(self) -> None:
        """Generator functions are analyzed for CQS."""
        code = EDGE_CASE_GENERATOR
        analyzer = PythonCQSAnalyzer()
        patterns = analyzer.analyze(code, "test.py", CQSConfig())
        gen_patterns = [p for p in patterns if p.function_name == "gen_example"]
        assert len(gen_patterns) == 1


class TestMinOperations:
    """Tests for min_operations configuration."""

    def test_min_operations_threshold(self) -> None:
        """Violation only flagged when >= min_operations of each type."""
        code = "def mixed():\n    x = query()\n    command(x)"
        analyzer = PythonCQSAnalyzer()
        # With min_operations=2, single INPUT + single OUTPUT is not a violation
        config = CQSConfig(min_operations=2)
        patterns = analyzer.analyze(code, "test.py", config)
        # The pattern exists but with min_operations=2 check, violation won't be flagged
        # at the linter level (not analyzer level)
        # At analyzer level, pattern still has 1 input and 1 output
        pattern = patterns[0] if patterns else None
        assert pattern is not None
        assert len(pattern.inputs) == 1
        assert len(pattern.outputs) == 1


class TestIgnorePatterns:
    """Tests for file path ignore patterns."""

    def test_ignore_pattern_match(self) -> None:
        """Files matching ignore_patterns are skipped at linter level."""
        # This is tested at the CQSRule level, not analyzer
        # The analyzer doesn't handle file path filtering
        code = CQS_VIOLATION_BASIC
        analyzer = PythonCQSAnalyzer()
        config = CQSConfig(ignore_patterns=["**/test_*.py"])
        # Analyzer still analyzes the code
        patterns = analyzer.analyze(code, "test_example.py", config)
        # The filtering happens in CQSRule.check(), not here
        assert len(patterns) >= 1


class TestErrorHandling:
    """Tests for error handling with malformed code."""

    def test_syntax_error_handled(self) -> None:
        """Syntax errors are handled gracefully."""
        code = "def broken(\n    x = query()"
        analyzer = PythonCQSAnalyzer()
        patterns = analyzer.analyze(code, "test.py", CQSConfig())
        # Should return empty list for syntax error
        assert patterns == []

    def test_empty_file_handled(self) -> None:
        """Empty file is handled gracefully."""
        code = ""
        analyzer = PythonCQSAnalyzer()
        patterns = analyzer.analyze(code, "test.py", CQSConfig())
        assert patterns == []

    def test_comments_only_handled(self) -> None:
        """File with only comments is handled gracefully."""
        code = "# This is a comment\n# Another comment"
        analyzer = PythonCQSAnalyzer()
        patterns = analyzer.analyze(code, "test.py", CQSConfig())
        assert patterns == []

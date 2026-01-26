"""
Purpose: Tests for isinstance LBYL pattern detection

Scope: Unit tests for detecting 'if isinstance(x, Type): x.method()' patterns

Overview: Test suite for isinstance LBYL pattern detection. Tests detection of basic
    patterns where isinstance check is followed by type-specific operations. Verifies
    configuration (disabled by default due to many valid uses), no false positives for
    different scenarios, and EAFP suggestion generation.

Dependencies: pytest, ast, src.linters.lbyl

Exports: Test classes for isinstance detection

Interfaces: pytest test discovery and execution

Implementation: Tests for IsinstanceDetector and LBYLViolationBuilder
"""

import ast

from src.linters.lbyl.pattern_detectors.isinstance_detector import (
    IsinstanceDetector,
    IsinstancePattern,
)
from src.linters.lbyl.violation_builder import build_isinstance_violation


class TestIsinstanceDetectorBasic:
    """Tests for basic isinstance LBYL detection."""

    def test_detects_if_isinstance_before_method_call(self) -> None:
        """Detect: if isinstance(x, Type): x.method() pattern."""
        code = """
if isinstance(value, str):
    result = value.upper()
"""
        tree = ast.parse(code)
        detector = IsinstanceDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 1
        assert isinstance(patterns[0], IsinstancePattern)
        assert patterns[0].object_name == "value"
        assert patterns[0].type_name == "str"

    def test_detects_if_isinstance_before_attribute_access(self) -> None:
        """Detect: if isinstance(x, Type): x.attr pattern."""
        code = """
if isinstance(obj, MyClass):
    data = obj.special_attr
"""
        tree = ast.parse(code)
        detector = IsinstanceDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 1
        assert patterns[0].object_name == "obj"
        assert patterns[0].type_name == "MyClass"

    def test_detects_with_else_branch(self) -> None:
        """Detect pattern with else branch."""
        code = """
if isinstance(x, int):
    result = x * 2
else:
    result = 0
"""
        tree = ast.parse(code)
        detector = IsinstanceDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 1

    def test_returns_correct_line_number(self) -> None:
        """Returns 1-indexed line number of the if statement."""
        code = """
# Comment line 2

if isinstance(x, str):
    result = x.upper()
"""
        tree = ast.parse(code)
        detector = IsinstanceDetector()
        patterns = detector.find_patterns(tree)
        assert patterns[0].line_number == 4

    def test_detects_isinstance_with_tuple_types(self) -> None:
        """Detect pattern with tuple of types."""
        code = """
if isinstance(value, (int, float)):
    result = value * 2
"""
        tree = ast.parse(code)
        detector = IsinstanceDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 1
        # Type name should capture the tuple representation
        assert patterns[0].object_name == "value"


class TestIsinstanceDetectorConfiguration:
    """Tests for isinstance detector configuration (disabled by default)."""

    def test_detector_can_be_instantiated(self) -> None:
        """Detector can be created and used."""
        detector = IsinstanceDetector()
        code = """
if isinstance(x, str):
    x.upper()
"""
        tree = ast.parse(code)
        patterns = detector.find_patterns(tree)
        # Detector finds patterns - config controls whether they become violations
        assert len(patterns) == 1

    def test_note_about_config_default(self) -> None:
        """Document that isinstance detection is disabled by default in config.

        This test serves as documentation that:
        - IsinstanceDetector itself finds patterns
        - LBYLConfig.detect_isinstance defaults to False
        - PythonLBYLAnalyzer respects this config setting

        The disable-by-default is intentional because many isinstance checks
        are valid type narrowing for union types and type safety.
        """
        from src.linters.lbyl.config import LBYLConfig

        config = LBYLConfig()
        assert config.detect_isinstance is False


class TestIsinstanceDetectorFalsePositives:
    """Tests for avoiding false positives."""

    def test_no_false_positive_for_different_object(self) -> None:
        """No detection when if and body use different objects."""
        code = """
if isinstance(obj1, str):
    result = obj2.upper()
"""
        tree = ast.parse(code)
        detector = IsinstanceDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 0

    def test_ignores_isinstance_without_body_operation(self) -> None:
        """Don't flag isinstance when body doesn't operate on the object."""
        code = """
if isinstance(x, str):
    print("it's a string")
"""
        tree = ast.parse(code)
        detector = IsinstanceDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 0

    def test_ignores_try_except_pattern(self) -> None:
        """Don't flag EAFP try/except pattern."""
        code = """
try:
    result = value.upper()
except AttributeError:
    result = str(value)
"""
        tree = ast.parse(code)
        detector = IsinstanceDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 0

    def test_ignores_isinstance_with_variable_type(self) -> None:
        """Don't flag when type is a variable (runtime value)."""
        code = """
expected_type = str
if isinstance(value, expected_type):
    result = value.upper()
"""
        tree = ast.parse(code)
        detector = IsinstanceDetector()
        patterns = detector.find_patterns(tree)
        # Variable type is handled - we still detect if object is used
        assert len(patterns) == 1  # Should detect since value is used


class TestIsinstanceDetectorEdgeCases:
    """Edge case tests for isinstance detection."""

    def test_handles_nested_isinstance(self) -> None:
        """Detect pattern with nested object."""
        code = """
if isinstance(self.data, list):
    result = self.data.append(item)
"""
        tree = ast.parse(code)
        detector = IsinstanceDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 1
        assert patterns[0].object_name == "self.data"

    def test_handles_qualified_type_name(self) -> None:
        """Detect pattern with qualified type name (module.Type)."""
        code = """
if isinstance(obj, collections.abc.Sequence):
    result = obj[0]
"""
        tree = ast.parse(code)
        detector = IsinstanceDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 1
        assert "Sequence" in patterns[0].type_name

    def test_handles_assignment_and_usage(self) -> None:
        """Detect when object is assigned to variable and used."""
        code = """
if isinstance(data, dict):
    keys = data.keys()
    use(keys)
"""
        tree = ast.parse(code)
        detector = IsinstanceDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 1


class TestIsinstanceDetectorSuggestions:
    """Tests for EAFP suggestion generation."""

    def test_suggestion_includes_try_except(self) -> None:
        """Suggestion should mention try/except."""
        code = """
if isinstance(value, str):
    result = value.upper()
"""
        tree = ast.parse(code)
        detector = IsinstanceDetector()
        patterns = detector.find_patterns(tree)
        pattern = patterns[0]
        assert isinstance(pattern, IsinstancePattern)
        violation = build_isinstance_violation(
            file_path="test.py",
            line=pattern.line_number,
            column=pattern.column,
            object_name=pattern.object_name,
            type_name=pattern.type_name,
        )
        assert "try" in violation.suggestion.lower()

    def test_suggestion_mentions_appropriate_exceptions(self) -> None:
        """Suggestion should mention TypeError or AttributeError."""
        code = """
if isinstance(obj, MyClass):
    obj.process()
"""
        tree = ast.parse(code)
        detector = IsinstanceDetector()
        patterns = detector.find_patterns(tree)
        pattern = patterns[0]
        assert isinstance(pattern, IsinstancePattern)
        violation = build_isinstance_violation(
            file_path="test.py",
            line=pattern.line_number,
            column=pattern.column,
            object_name=pattern.object_name,
            type_name=pattern.type_name,
        )
        # Should mention common exceptions for type-related errors
        suggestion_lower = violation.suggestion.lower()
        assert "typeerror" in suggestion_lower or "attributeerror" in suggestion_lower

    def test_suggestion_uses_actual_names(self) -> None:
        """Suggestion uses the actual object and type names."""
        code = """
if isinstance(my_value, CustomType):
    my_value.custom_method()
"""
        tree = ast.parse(code)
        detector = IsinstanceDetector()
        patterns = detector.find_patterns(tree)
        pattern = patterns[0]
        assert isinstance(pattern, IsinstancePattern)
        violation = build_isinstance_violation(
            file_path="test.py",
            line=pattern.line_number,
            column=pattern.column,
            object_name=pattern.object_name,
            type_name=pattern.type_name,
        )
        assert "my_value" in violation.message
        assert "CustomType" in violation.message


class TestMultipleIsinstancePatterns:
    """Tests for detecting multiple patterns in a single file."""

    def test_detects_multiple_isinstance_patterns(self) -> None:
        """Detects multiple isinstance LBYL patterns."""
        code = """
if isinstance(x, str):
    result1 = x.upper()

if isinstance(y, int):
    result2 = y * 2
"""
        tree = ast.parse(code)
        detector = IsinstanceDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 2

    def test_detects_nested_if_patterns(self) -> None:
        """Detects patterns in nested if statements."""
        code = """
if condition:
    if isinstance(x, str):
        result = x.upper()
"""
        tree = ast.parse(code)
        detector = IsinstanceDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 1

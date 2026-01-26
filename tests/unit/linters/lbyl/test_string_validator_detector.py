"""
Purpose: Tests for string validator LBYL pattern detection

Scope: Unit tests for detecting 'if s.isnumeric(): int(s)' patterns

Overview: Test suite for string validation LBYL pattern detection. Tests detection of
    patterns where code checks string content before conversion (e.g., isnumeric/isdigit
    before int(), isalpha before processing). Verifies no false positives for different
    variables and proper EAFP suggestion generation. Covers methods: isnumeric, isdigit,
    isalpha, isdecimal.

Dependencies: pytest, ast, src.linters.lbyl

Exports: Test classes for string validator detection

Interfaces: pytest test discovery and execution

Implementation: Tests for StringValidatorDetector and violation builder
"""

import ast

from src.linters.lbyl.pattern_detectors.string_validator_detector import (
    StringValidatorDetector,
    StringValidatorPattern,
)
from src.linters.lbyl.violation_builder import build_string_validator_violation


class TestStringValidatorDetectorBasic:
    """Tests for basic string validator LBYL detection."""

    def test_detects_isnumeric_before_int(self) -> None:
        """Detect: if s.isnumeric(): int(s) pattern."""
        code = """
if value.isnumeric():
    result = int(value)
"""
        tree = ast.parse(code)
        detector = StringValidatorDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 1
        assert isinstance(patterns[0], StringValidatorPattern)
        assert patterns[0].string_name == "value"
        assert patterns[0].validator_method == "isnumeric"
        assert patterns[0].conversion_func == "int"

    def test_detects_isdigit_before_int(self) -> None:
        """Detect: if s.isdigit(): int(s) pattern."""
        code = """
if text.isdigit():
    number = int(text)
"""
        tree = ast.parse(code)
        detector = StringValidatorDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 1
        assert patterns[0].validator_method == "isdigit"

    def test_detects_isdecimal_before_float(self) -> None:
        """Detect: if s.isdecimal(): float(s) pattern."""
        code = """
if num_str.isdecimal():
    value = float(num_str)
"""
        tree = ast.parse(code)
        detector = StringValidatorDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 1
        assert patterns[0].validator_method == "isdecimal"
        assert patterns[0].conversion_func == "float"

    def test_detects_isnumeric_before_float(self) -> None:
        """Detect: if s.isnumeric(): float(s) pattern."""
        code = """
if input_str.isnumeric():
    parsed = float(input_str)
"""
        tree = ast.parse(code)
        detector = StringValidatorDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 1
        assert patterns[0].conversion_func == "float"

    def test_returns_correct_line_number(self) -> None:
        """Returns 1-indexed line number of the if statement."""
        code = """
# Comment

if s.isnumeric():
    n = int(s)
"""
        tree = ast.parse(code)
        detector = StringValidatorDetector()
        patterns = detector.find_patterns(tree)
        assert patterns[0].line_number == 4


class TestStringValidatorDetectorFalsePositives:
    """Tests for avoiding false positives."""

    def test_no_false_positive_for_different_variable(self) -> None:
        """No detection when check and conversion use different variables."""
        code = """
if x.isnumeric():
    n = int(y)
"""
        tree = ast.parse(code)
        detector = StringValidatorDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 0

    def test_ignores_try_except_valueerror(self) -> None:
        """Don't flag EAFP try/except pattern."""
        code = """
try:
    n = int(s)
except ValueError:
    n = 0
"""
        tree = ast.parse(code)
        detector = StringValidatorDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 0

    def test_ignores_validation_without_conversion(self) -> None:
        """Don't flag validation check without subsequent conversion."""
        code = """
if s.isnumeric():
    print("it's a number")
"""
        tree = ast.parse(code)
        detector = StringValidatorDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 0

    def test_ignores_non_validator_method(self) -> None:
        """Don't flag non-validator string methods."""
        code = """
if s.startswith("0"):
    n = int(s)
"""
        tree = ast.parse(code)
        detector = StringValidatorDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 0

    def test_ignores_isalpha_with_int(self) -> None:
        """Don't flag isalpha before int (doesn't make sense)."""
        code = """
if s.isalpha():
    n = int(s)
"""
        tree = ast.parse(code)
        detector = StringValidatorDetector()
        patterns = detector.find_patterns(tree)
        # isalpha() followed by int() is not a typical pattern
        assert len(patterns) == 0


class TestStringValidatorDetectorEdgeCases:
    """Edge case tests for string validator detection."""

    def test_handles_method_chain_variable(self) -> None:
        """Detect pattern with chained method calls on result."""
        code = """
if text.strip().isnumeric():
    n = int(text.strip())
"""
        tree = ast.parse(code)
        detector = StringValidatorDetector()
        patterns = detector.find_patterns(tree)
        # Should detect the pattern with chained call
        assert len(patterns) == 1

    def test_handles_attribute_string(self) -> None:
        """Detect pattern with attribute access on object."""
        code = """
if self.value.isnumeric():
    n = int(self.value)
"""
        tree = ast.parse(code)
        detector = StringValidatorDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 1
        assert patterns[0].string_name == "self.value"

    def test_handles_subscript_string(self) -> None:
        """Detect pattern with subscript access."""
        code = """
if data[0].isnumeric():
    n = int(data[0])
"""
        tree = ast.parse(code)
        detector = StringValidatorDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 1

    def test_handles_nested_conversion(self) -> None:
        """Detect pattern where conversion is inside expression."""
        code = """
if s.isnumeric():
    result = abs(int(s))
"""
        tree = ast.parse(code)
        detector = StringValidatorDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 1


class TestStringValidatorDetectorSuggestions:
    """Tests for EAFP suggestion generation."""

    def test_suggestion_mentions_try_except(self) -> None:
        """Suggestion should mention try/except pattern."""
        code = """
if s.isnumeric():
    n = int(s)
"""
        tree = ast.parse(code)
        detector = StringValidatorDetector()
        patterns = detector.find_patterns(tree)
        pattern = patterns[0]
        assert isinstance(pattern, StringValidatorPattern)
        violation = build_string_validator_violation(
            file_path="test.py",
            line=pattern.line_number,
            column=pattern.column,
            string_name=pattern.string_name,
            validator_method=pattern.validator_method,
            conversion_func=pattern.conversion_func,
        )
        assert "try" in violation.suggestion.lower()
        assert "ValueError" in violation.suggestion

    def test_suggestion_uses_actual_variable_name(self) -> None:
        """Suggestion uses the actual variable name."""
        code = """
if user_input.isnumeric():
    age = int(user_input)
"""
        tree = ast.parse(code)
        detector = StringValidatorDetector()
        patterns = detector.find_patterns(tree)
        pattern = patterns[0]
        assert isinstance(pattern, StringValidatorPattern)
        violation = build_string_validator_violation(
            file_path="test.py",
            line=pattern.line_number,
            column=pattern.column,
            string_name=pattern.string_name,
            validator_method=pattern.validator_method,
            conversion_func=pattern.conversion_func,
        )
        assert "user_input" in violation.suggestion
        assert "int" in violation.suggestion


class TestMultipleStringValidatorPatterns:
    """Tests for detecting multiple patterns in a single file."""

    def test_detects_multiple_patterns(self) -> None:
        """Detects multiple string validator LBYL patterns."""
        code = """
if a.isnumeric():
    x = int(a)

if b.isdigit():
    y = int(b)
"""
        tree = ast.parse(code)
        detector = StringValidatorDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 2

    def test_detects_nested_if_patterns(self) -> None:
        """Detects patterns in nested if statements."""
        code = """
if condition:
    if s.isnumeric():
        n = int(s)
"""
        tree = ast.parse(code)
        detector = StringValidatorDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 1

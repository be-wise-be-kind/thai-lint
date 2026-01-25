"""
Purpose: Tests for division check LBYL pattern detection

Scope: Unit tests for detecting 'if x != 0: a / x' patterns

Overview: Test suite for division check LBYL pattern detection. Tests detection of
    patterns where code checks if a divisor is non-zero before performing division.
    Covers patterns like 'if x != 0: a / x', 'if 0 != x:', 'if x == 0: else: a / x',
    and truthy checks 'if x:'. Tests division, integer division, modulo, and augmented
    assignment operators.

Dependencies: pytest, ast, src.linters.lbyl

Exports: Test classes for division check detection

Interfaces: pytest test discovery and execution

Implementation: Tests for DivisionCheckDetector and violation builder
"""

import ast

from src.linters.lbyl.pattern_detectors.division_check_detector import (
    DivisionCheckDetector,
    DivisionCheckPattern,
)
from src.linters.lbyl.violation_builder import build_division_check_violation


class TestDivisionCheckDetectorBasic:
    """Tests for basic division check LBYL detection."""

    def test_detects_not_equal_zero_before_division(self) -> None:
        """Detect: if x != 0: a / x pattern."""
        code = """
if divisor != 0:
    result = numerator / divisor
"""
        tree = ast.parse(code)
        detector = DivisionCheckDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 1
        assert isinstance(patterns[0], DivisionCheckPattern)
        assert patterns[0].divisor_name == "divisor"
        assert patterns[0].operation == "/"

    def test_detects_zero_not_equal_before_division(self) -> None:
        """Detect: if 0 != x: a / x pattern (reversed)."""
        code = """
if 0 != value:
    result = 100 / value
"""
        tree = ast.parse(code)
        detector = DivisionCheckDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 1
        assert patterns[0].divisor_name == "value"

    def test_detects_equal_zero_with_else(self) -> None:
        """Detect: if x == 0: ... else: a / x pattern."""
        code = """
if divisor == 0:
    result = default
else:
    result = numerator / divisor
"""
        tree = ast.parse(code)
        detector = DivisionCheckDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 1
        assert patterns[0].divisor_name == "divisor"

    def test_detects_truthy_check_before_division(self) -> None:
        """Detect: if x: a / x pattern (truthy check)."""
        code = """
if count:
    average = total / count
"""
        tree = ast.parse(code)
        detector = DivisionCheckDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 1
        assert patterns[0].divisor_name == "count"

    def test_returns_correct_line_number(self) -> None:
        """Returns 1-indexed line number of the if statement."""
        code = """
# Comment

if x != 0:
    y = 10 / x
"""
        tree = ast.parse(code)
        detector = DivisionCheckDetector()
        patterns = detector.find_patterns(tree)
        assert patterns[0].line_number == 4


class TestDivisionCheckDetectorOperators:
    """Tests for different division-related operators."""

    def test_detects_integer_division(self) -> None:
        """Detect pattern with integer division //."""
        code = """
if n != 0:
    result = total // n
"""
        tree = ast.parse(code)
        detector = DivisionCheckDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 1
        assert patterns[0].operation == "//"

    def test_detects_modulo(self) -> None:
        """Detect pattern with modulo %."""
        code = """
if divisor != 0:
    remainder = value % divisor
"""
        tree = ast.parse(code)
        detector = DivisionCheckDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 1
        assert patterns[0].operation == "%"

    def test_detects_augmented_division(self) -> None:
        """Detect pattern with /= operator."""
        code = """
if x != 0:
    value /= x
"""
        tree = ast.parse(code)
        detector = DivisionCheckDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 1
        assert patterns[0].operation == "/="

    def test_detects_augmented_int_division(self) -> None:
        """Detect pattern with //= operator."""
        code = """
if n != 0:
    counter //= n
"""
        tree = ast.parse(code)
        detector = DivisionCheckDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 1
        assert patterns[0].operation == "//="

    def test_detects_augmented_modulo(self) -> None:
        """Detect pattern with %= operator."""
        code = """
if mod != 0:
    result %= mod
"""
        tree = ast.parse(code)
        detector = DivisionCheckDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 1
        assert patterns[0].operation == "%="


class TestDivisionCheckDetectorFalsePositives:
    """Tests for avoiding false positives."""

    def test_no_false_positive_for_different_variable(self) -> None:
        """No detection when check and division use different variables."""
        code = """
if x != 0:
    result = a / y
"""
        tree = ast.parse(code)
        detector = DivisionCheckDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 0

    def test_ignores_try_except_zerodivisionerror(self) -> None:
        """Don't flag EAFP try/except pattern."""
        code = """
try:
    result = a / x
except ZeroDivisionError:
    result = 0
"""
        tree = ast.parse(code)
        detector = DivisionCheckDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 0

    def test_ignores_zero_check_without_division(self) -> None:
        """Don't flag zero check when body doesn't divide by checked variable."""
        code = """
if x != 0:
    result = x + 1
"""
        tree = ast.parse(code)
        detector = DivisionCheckDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 0

    def test_ignores_non_zero_comparison(self) -> None:
        """Don't flag comparisons not involving zero."""
        code = """
if x != 1:
    result = a / x
"""
        tree = ast.parse(code)
        detector = DivisionCheckDetector()
        patterns = detector.find_patterns(tree)
        # Comparing to 1, not 0 - should not flag
        assert len(patterns) == 0

    def test_ignores_pathlib_division_with_path_root(self) -> None:
        """Don't flag pathlib path joining (project_root / file)."""
        code = """
if layout_file:
    return project_root / layout_file
"""
        tree = ast.parse(code)
        detector = DivisionCheckDetector()
        patterns = detector.find_patterns(tree)
        # Should not detect - this is pathlib, not numeric division
        assert len(patterns) == 0

    def test_ignores_pathlib_division_with_base_path(self) -> None:
        """Don't flag pathlib path joining (base_path / subdir)."""
        code = """
if subdir:
    result = base_path / subdir
"""
        tree = ast.parse(code)
        detector = DivisionCheckDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 0

    def test_ignores_pathlib_division_with_file_name(self) -> None:
        """Don't flag pathlib path joining when divisor is file-related."""
        code = """
if file_name:
    result = directory / file_name
"""
        tree = ast.parse(code)
        detector = DivisionCheckDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 0

    def test_still_detects_numeric_division_with_generic_names(self) -> None:
        """Still detect numeric division when names don't suggest paths."""
        code = """
if divisor != 0:
    result = numerator / divisor
"""
        tree = ast.parse(code)
        detector = DivisionCheckDetector()
        patterns = detector.find_patterns(tree)
        # Should detect - these are generic numeric names
        assert len(patterns) == 1


class TestDivisionCheckDetectorEdgeCases:
    """Edge case tests for division check detection."""

    def test_handles_attribute_divisor(self) -> None:
        """Detect pattern with attribute access as divisor."""
        code = """
if self.count != 0:
    avg = total / self.count
"""
        tree = ast.parse(code)
        detector = DivisionCheckDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 1
        assert patterns[0].divisor_name == "self.count"

    def test_handles_subscript_divisor(self) -> None:
        """Detect pattern with subscript as divisor."""
        code = """
if data[0] != 0:
    result = value / data[0]
"""
        tree = ast.parse(code)
        detector = DivisionCheckDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 1

    def test_handles_nested_division(self) -> None:
        """Detect pattern where division is nested in expression."""
        code = """
if n != 0:
    result = abs(total / n)
"""
        tree = ast.parse(code)
        detector = DivisionCheckDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 1

    def test_handles_multiple_divisions_same_divisor(self) -> None:
        """Detect single pattern when same divisor used multiple times."""
        code = """
if x != 0:
    a = y / x
    b = z / x
"""
        tree = ast.parse(code)
        detector = DivisionCheckDetector()
        patterns = detector.find_patterns(tree)
        # Should detect as single pattern for the if statement
        assert len(patterns) == 1


class TestDivisionCheckDetectorSuggestions:
    """Tests for EAFP suggestion generation."""

    def test_suggestion_mentions_try_except(self) -> None:
        """Suggestion should mention try/except pattern."""
        code = """
if x != 0:
    result = a / x
"""
        tree = ast.parse(code)
        detector = DivisionCheckDetector()
        patterns = detector.find_patterns(tree)
        pattern = patterns[0]
        assert isinstance(pattern, DivisionCheckPattern)
        violation = build_division_check_violation(
            file_path="test.py",
            line=pattern.line_number,
            column=pattern.column,
            divisor_name=pattern.divisor_name,
            operation=pattern.operation,
        )
        assert "try" in violation.suggestion.lower()
        assert "ZeroDivisionError" in violation.suggestion

    def test_suggestion_uses_actual_variable_name(self) -> None:
        """Suggestion uses the actual variable name."""
        code = """
if item_count != 0:
    average = total / item_count
"""
        tree = ast.parse(code)
        detector = DivisionCheckDetector()
        patterns = detector.find_patterns(tree)
        pattern = patterns[0]
        assert isinstance(pattern, DivisionCheckPattern)
        violation = build_division_check_violation(
            file_path="test.py",
            line=pattern.line_number,
            column=pattern.column,
            divisor_name=pattern.divisor_name,
            operation=pattern.operation,
        )
        assert "item_count" in violation.suggestion


class TestMultipleDivisionCheckPatterns:
    """Tests for detecting multiple patterns in a single file."""

    def test_detects_multiple_patterns(self) -> None:
        """Detects multiple division check LBYL patterns."""
        code = """
if a != 0:
    x = 10 / a

if b != 0:
    y = 20 / b
"""
        tree = ast.parse(code)
        detector = DivisionCheckDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 2

    def test_detects_nested_if_patterns(self) -> None:
        """Detects patterns in nested if statements."""
        code = """
if condition:
    if x != 0:
        result = y / x
"""
        tree = ast.parse(code)
        detector = DivisionCheckDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 1

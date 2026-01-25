"""
Purpose: Tests for None check LBYL pattern detection

Scope: Unit tests for detecting 'if x is not None: x.method()' patterns

Overview: Test suite for None check LBYL pattern detection. Tests detection of patterns
    where code checks if a variable is not None before using it. Includes tests for
    'is not None' checks followed by method calls or attribute access. Verifies no false
    positives for different variables, walrus operator usage, and type narrowing cases.
    Tests EAFP suggestion generation.

Dependencies: pytest, ast, src.linters.lbyl

Exports: Test classes for None check detection

Interfaces: pytest test discovery and execution

Implementation: Tests for NoneCheckDetector and violation builder
"""

import ast

from src.linters.lbyl.pattern_detectors.none_check_detector import (
    NoneCheckDetector,
    NoneCheckPattern,
)
from src.linters.lbyl.violation_builder import build_none_check_violation


class TestNoneCheckDetectorBasic:
    """Tests for basic None check LBYL detection."""

    def test_detects_is_not_none_before_method_call(self) -> None:
        """Detect: if x is not None: x.method() pattern."""
        code = """
if value is not None:
    value.process()
"""
        tree = ast.parse(code)
        detector = NoneCheckDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 1
        assert isinstance(patterns[0], NoneCheckPattern)
        assert patterns[0].variable_name == "value"

    def test_detects_is_not_none_before_attribute_access(self) -> None:
        """Detect: if x is not None: y = x.attr pattern."""
        code = """
if config is not None:
    setting = config.debug
"""
        tree = ast.parse(code)
        detector = NoneCheckDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 1
        assert patterns[0].variable_name == "config"

    def test_detects_is_none_with_else(self) -> None:
        """Detect: if x is None: ... else: x.method() pattern."""
        code = """
if handler is None:
    default_action()
else:
    handler.process()
"""
        tree = ast.parse(code)
        detector = NoneCheckDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 1
        assert patterns[0].variable_name == "handler"

    def test_returns_correct_line_number(self) -> None:
        """Returns 1-indexed line number of the if statement."""
        code = """
# Comment line 2

if obj is not None:
    obj.do_work()
"""
        tree = ast.parse(code)
        detector = NoneCheckDetector()
        patterns = detector.find_patterns(tree)
        assert patterns[0].line_number == 4

    def test_detects_none_is_not_variable(self) -> None:
        """Detect: if None is not x: x.method() pattern (reverse order)."""
        code = """
if None is not result:
    result.save()
"""
        tree = ast.parse(code)
        detector = NoneCheckDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 1
        assert patterns[0].variable_name == "result"


class TestNoneCheckDetectorFalsePositives:
    """Tests for avoiding false positives."""

    def test_no_false_positive_for_different_variable(self) -> None:
        """No detection when check and usage are different variables."""
        code = """
if x is not None:
    y.process()
"""
        tree = ast.parse(code)
        detector = NoneCheckDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 0

    def test_ignores_walrus_operator_assignment(self) -> None:
        """Don't flag walrus operator patterns - they're assignment, not LBYL."""
        code = """
if (result := get_result()) is not None:
    result.process()
"""
        tree = ast.parse(code)
        detector = NoneCheckDetector()
        patterns = detector.find_patterns(tree)
        # Walrus assigns value, so it's not a classic LBYL check
        assert len(patterns) == 0

    def test_ignores_try_except_attributeerror(self) -> None:
        """Don't flag EAFP try/except pattern."""
        code = """
try:
    value.process()
except AttributeError:
    pass
"""
        tree = ast.parse(code)
        detector = NoneCheckDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 0

    def test_ignores_none_check_without_usage(self) -> None:
        """Don't flag None check when body doesn't use the variable."""
        code = """
if value is not None:
    print("value exists")
"""
        tree = ast.parse(code)
        detector = NoneCheckDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 0

    def test_ignores_comparison_not_involving_none(self) -> None:
        """Don't flag non-None comparisons."""
        code = """
if x is not y:
    x.process()
"""
        tree = ast.parse(code)
        detector = NoneCheckDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 0

    def test_ignores_equality_check(self) -> None:
        """Don't flag == None checks (should use 'is')."""
        code = """
if x == None:
    x.process()
"""
        tree = ast.parse(code)
        detector = NoneCheckDetector()
        patterns = detector.find_patterns(tree)
        # Only detect 'is' comparisons, not '=='
        assert len(patterns) == 0


class TestNoneCheckDetectorEdgeCases:
    """Edge case tests for None check detection."""

    def test_handles_nested_object(self) -> None:
        """Detect pattern with nested object access."""
        code = """
if self.handler is not None:
    self.handler.process()
"""
        tree = ast.parse(code)
        detector = NoneCheckDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 1
        assert patterns[0].variable_name == "self.handler"

    def test_handles_subscript_access(self) -> None:
        """Detect pattern where body uses subscript on checked variable."""
        code = """
if data is not None:
    value = data[0]
"""
        tree = ast.parse(code)
        detector = NoneCheckDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 1

    def test_handles_call_on_variable(self) -> None:
        """Detect pattern where checked variable is called."""
        code = """
if callback is not None:
    callback()
"""
        tree = ast.parse(code)
        detector = NoneCheckDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 1
        assert patterns[0].variable_name == "callback"

    def test_handles_chained_attribute_access(self) -> None:
        """Detect pattern with chained attributes in body."""
        code = """
if obj is not None:
    obj.logger.info("message")
"""
        tree = ast.parse(code)
        detector = NoneCheckDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 1


class TestNoneCheckDetectorSuggestions:
    """Tests for EAFP suggestion generation."""

    def test_suggestion_mentions_try_except(self) -> None:
        """Suggestion should mention try/except pattern."""
        code = """
if handler is not None:
    handler.process()
"""
        tree = ast.parse(code)
        detector = NoneCheckDetector()
        patterns = detector.find_patterns(tree)
        pattern = patterns[0]
        assert isinstance(pattern, NoneCheckPattern)
        violation = build_none_check_violation(
            file_path="test.py",
            line=pattern.line_number,
            column=pattern.column,
            variable_name=pattern.variable_name,
        )
        assert "try" in violation.suggestion.lower()
        assert "AttributeError" in violation.suggestion

    def test_suggestion_uses_actual_variable_name(self) -> None:
        """Suggestion uses the actual variable name."""
        code = """
if my_handler is not None:
    my_handler.process()
"""
        tree = ast.parse(code)
        detector = NoneCheckDetector()
        patterns = detector.find_patterns(tree)
        pattern = patterns[0]
        assert isinstance(pattern, NoneCheckPattern)
        violation = build_none_check_violation(
            file_path="test.py",
            line=pattern.line_number,
            column=pattern.column,
            variable_name=pattern.variable_name,
        )
        assert "my_handler" in violation.suggestion


class TestMultipleNoneCheckPatterns:
    """Tests for detecting multiple patterns in a single file."""

    def test_detects_multiple_none_check_patterns(self) -> None:
        """Detects multiple None check LBYL patterns."""
        code = """
if a is not None:
    a.process()

if b is not None:
    b.execute()
"""
        tree = ast.parse(code)
        detector = NoneCheckDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 2

    def test_detects_nested_if_patterns(self) -> None:
        """Detects patterns in nested if statements."""
        code = """
if condition:
    if obj is not None:
        obj.work()
"""
        tree = ast.parse(code)
        detector = NoneCheckDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 1

"""
Purpose: Tests for len check LBYL pattern detection

Scope: Unit tests for detecting 'if len(lst) > i: lst[i]' patterns

Overview: Test suite for len check LBYL pattern detection. Tests detection of patterns
    where length is checked before index access using various comparison operators
    (>, >=, <, <=). Verifies no false positives for different list/index combinations
    and EAFP suggestion generation using try/except IndexError.

Dependencies: pytest, ast, src.linters.lbyl

Exports: Test classes for len check detection

Interfaces: pytest test discovery and execution

Implementation: Tests for LenCheckDetector and LBYLViolationBuilder
"""

import ast

from src.linters.lbyl.pattern_detectors.len_check_detector import (
    LenCheckDetector,
    LenCheckPattern,
)
from src.linters.lbyl.violation_builder import build_len_check_violation


class TestLenCheckDetectorBasic:
    """Tests for basic len check LBYL detection."""

    def test_detects_len_greater_before_index(self) -> None:
        """Detect: if len(lst) > i: lst[i] pattern."""
        code = """
if len(items) > index:
    value = items[index]
"""
        tree = ast.parse(code)
        detector = LenCheckDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 1
        assert isinstance(patterns[0], LenCheckPattern)
        assert patterns[0].collection_name == "items"

    def test_detects_len_gte_before_index(self) -> None:
        """Detect: if len(lst) >= i+1: lst[i] pattern with variable index."""
        code = """
if len(items) >= idx + 1:
    value = items[idx]
"""
        tree = ast.parse(code)
        detector = LenCheckDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 1

    def test_detects_index_less_than_len(self) -> None:
        """Detect: if i < len(lst): lst[i] pattern."""
        code = """
if index < len(items):
    value = items[index]
"""
        tree = ast.parse(code)
        detector = LenCheckDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 1
        assert patterns[0].collection_name == "items"

    def test_detects_index_lte_len(self) -> None:
        """Detect: if i <= len(lst) - 1: lst[i] pattern."""
        code = """
if index <= len(items) - 1:
    value = items[index]
"""
        tree = ast.parse(code)
        detector = LenCheckDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 1

    def test_returns_correct_line_number(self) -> None:
        """Returns 1-indexed line number of the if statement."""
        code = """
# Comment line

if len(items) > idx:
    value = items[idx]
"""
        tree = ast.parse(code)
        detector = LenCheckDetector()
        patterns = detector.find_patterns(tree)
        assert patterns[0].line_number == 4

    def test_detects_with_else_branch(self) -> None:
        """Detect pattern with else branch."""
        code = """
if len(items) > index:
    value = items[index]
else:
    value = None
"""
        tree = ast.parse(code)
        detector = LenCheckDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 1


class TestLenCheckDetectorComparisons:
    """Tests for various comparison operator handling."""

    def test_detects_len_gt_variable_index(self) -> None:
        """Detect: if len(lst) > idx: lst[idx] pattern with variable."""
        code = """
if len(items) > idx:
    first = items[idx]
"""
        tree = ast.parse(code)
        detector = LenCheckDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 1

    def test_detects_len_check_with_variable_index(self) -> None:
        """Detect: if len(lst) >= pos: lst[pos] pattern with variable."""
        code = """
if len(items) >= pos:
    third = items[pos]
"""
        tree = ast.parse(code)
        detector = LenCheckDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 1

    def test_detects_reversed_comparison_with_variable(self) -> None:
        """Detect: if idx < len(lst): lst[idx] pattern with variable."""
        code = """
if idx < len(items):
    first = items[idx]
"""
        tree = ast.parse(code)
        detector = LenCheckDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 1


class TestLenCheckDetectorFalsePositives:
    """Tests for avoiding false positives."""

    def test_no_false_positive_for_different_list(self) -> None:
        """No detection when len and access use different lists."""
        code = """
if len(list1) > idx:
    value = list2[idx]
"""
        tree = ast.parse(code)
        detector = LenCheckDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 0

    def test_ignores_len_check_without_index_access(self) -> None:
        """Don't flag len check when body doesn't access by index."""
        code = """
if len(items) > 0:
    print("List has items")
"""
        tree = ast.parse(code)
        detector = LenCheckDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 0

    def test_ignores_equality_check(self) -> None:
        """Don't flag equality checks like if len(lst) == 0."""
        code = """
if len(items) == 0:
    items.append("default")
"""
        tree = ast.parse(code)
        detector = LenCheckDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 0

    def test_ignores_not_equal_check(self) -> None:
        """Don't flag not equal checks like if len(lst) != 0."""
        code = """
if len(items) != 0:
    process(items)
"""
        tree = ast.parse(code)
        detector = LenCheckDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 0

    def test_ignores_constant_index_zero(self) -> None:
        """Don't flag constant index checks - they're local validation."""
        code = """
if len(items) > 0:
    first = items[0]
"""
        tree = ast.parse(code)
        detector = LenCheckDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 0

    def test_ignores_constant_index_positive(self) -> None:
        """Don't flag constant index checks like lst[2]."""
        code = """
if len(items) >= 3:
    third = items[2]
"""
        tree = ast.parse(code)
        detector = LenCheckDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 0

    def test_ignores_constant_negative_index(self) -> None:
        """Don't flag constant negative index checks like lst[-1]."""
        code = """
if len(items) >= 1:
    last = items[-1]
"""
        tree = ast.parse(code)
        detector = LenCheckDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 0

    def test_ignores_constant_expression_index(self) -> None:
        """Don't flag computed constant index checks like lst[len(lst) - 1]."""
        code = """
if len(items) > 0:
    value = items[len(items) - 1]
"""
        tree = ast.parse(code)
        detector = LenCheckDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 0


class TestLenCheckDetectorEdgeCases:
    """Edge case tests for len check detection."""

    def test_handles_nested_list_access(self) -> None:
        """Detect when list is attribute: if len(self.items) > i: self.items[i]."""
        code = """
if len(self.items) > index:
    value = self.items[index]
"""
        tree = ast.parse(code)
        detector = LenCheckDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 1
        assert patterns[0].collection_name == "self.items"

    def test_handles_method_call_list(self) -> None:
        """Detect when list comes from method: if len(get_items()) > i: get_items()[i]."""
        code = """
if len(get_items()) > idx:
    value = get_items()[idx]
"""
        tree = ast.parse(code)
        detector = LenCheckDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 1

    def test_handles_subscript_in_nested_statement(self) -> None:
        """Detect when subscript is in nested statement."""
        code = """
if len(items) > idx:
    for item in items:
        if items[idx] == item:
            pass
"""
        tree = ast.parse(code)
        detector = LenCheckDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 1


class TestLenCheckDetectorSuggestions:
    """Tests for EAFP suggestion generation."""

    def test_suggestion_includes_try_except_indexerror(self) -> None:
        """Suggestion should mention try/except IndexError."""
        code = """
if len(items) > index:
    value = items[index]
"""
        tree = ast.parse(code)
        detector = LenCheckDetector()
        patterns = detector.find_patterns(tree)
        pattern = patterns[0]
        assert isinstance(pattern, LenCheckPattern)
        violation = build_len_check_violation(
            file_path="test.py",
            line=pattern.line_number,
            column=pattern.column,
            collection_name=pattern.collection_name,
            index_expression=pattern.index_expression,
        )
        assert "try" in violation.suggestion.lower()
        assert "IndexError" in violation.suggestion

    def test_suggestion_uses_actual_list_name(self) -> None:
        """Suggestion uses the actual list variable name."""
        code = """
if len(my_data_list) > pos:
    value = my_data_list[pos]
"""
        tree = ast.parse(code)
        detector = LenCheckDetector()
        patterns = detector.find_patterns(tree)
        pattern = patterns[0]
        assert isinstance(pattern, LenCheckPattern)
        violation = build_len_check_violation(
            file_path="test.py",
            line=pattern.line_number,
            column=pattern.column,
            collection_name=pattern.collection_name,
            index_expression=pattern.index_expression,
        )
        assert "my_data_list" in violation.suggestion


class TestMultipleLenCheckPatterns:
    """Tests for detecting multiple patterns."""

    def test_detects_multiple_len_check_patterns(self) -> None:
        """Detects multiple len check LBYL patterns with variable indices."""
        code = """
if len(items1) > idx1:
    value1 = items1[idx1]

if len(items2) > index:
    value2 = items2[index]
"""
        tree = ast.parse(code)
        detector = LenCheckDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 2

    def test_detects_nested_if_patterns(self) -> None:
        """Detects patterns in nested if statements."""
        code = """
if condition:
    if len(items) > idx:
        value = items[idx]
"""
        tree = ast.parse(code)
        detector = LenCheckDetector()
        patterns = detector.find_patterns(tree)
        assert len(patterns) == 1

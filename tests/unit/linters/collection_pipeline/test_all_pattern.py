"""
Purpose: Test detection of all() anti-patterns

Scope: Unit tests for detecting loops that should use all() builtin

Overview: Comprehensive test suite for detecting loops that return False on first non-match
    and True at the end, which can be refactored to all(). Tests cover basic patterns,
    edge cases, and false positive prevention. Follows TDD methodology.

Dependencies: pytest, src.linters.collection_pipeline.detector

Exports: TestAllPatternBasic, TestAllPatternEdgeCases, TestAllPatternNoViolation

Interfaces: Standard pytest test classes with test methods

Implementation: TDD test cases for all() pattern detection
"""

from src.linters.collection_pipeline.detector import (
    PatternType,
    PipelinePatternDetector,
)


class TestAllPatternBasic:
    """Tests for detection of basic all() patterns."""

    def test_detects_basic_all_pattern_with_not(self) -> None:
        """Detect: for x in iter: if not cond(x): return False; return True."""
        code = """
def all_valid(items):
    for item in items:
        if not item.is_valid():
            return False
    return True
"""
        detector = PipelinePatternDetector(code)
        matches = detector.detect_patterns()

        assert len(matches) == 1
        assert matches[0].pattern_type == PatternType.ALL_PATTERN
        assert matches[0].loop_var == "item"
        assert matches[0].iterable == "items"
        assert "all(" in matches[0].suggestion

    def test_detects_all_pattern_with_positive_condition(self) -> None:
        """Detect: for x in iter: if cond(x): return False; return True (positive cond)."""
        code = """
def none_invalid(items):
    for item in items:
        if item.is_invalid():
            return False
    return True
"""
        detector = PipelinePatternDetector(code)
        matches = detector.detect_patterns()

        assert len(matches) == 1
        assert matches[0].pattern_type == PatternType.ALL_PATTERN

    def test_detects_all_pattern_with_comparison(self) -> None:
        """Detect all pattern with comparison condition."""
        code = """
def all_positive(numbers):
    for num in numbers:
        if num <= 0:
            return False
    return True
"""
        detector = PipelinePatternDetector(code)
        matches = detector.detect_patterns()

        assert len(matches) == 1
        assert matches[0].pattern_type == PatternType.ALL_PATTERN

    def test_detects_all_pattern_with_isinstance(self) -> None:
        """Detect all pattern with isinstance check."""
        code = """
def all_strings(items):
    for item in items:
        if not isinstance(item, str):
            return False
    return True
"""
        detector = PipelinePatternDetector(code)
        matches = detector.detect_patterns()

        assert len(matches) == 1
        assert matches[0].pattern_type == PatternType.ALL_PATTERN


class TestAllPatternCompoundConditions:
    """Tests for all() patterns with compound conditions."""

    def test_detects_all_pattern_with_or_condition(self) -> None:
        """Detect all pattern with 'or' condition (any failure returns False)."""
        code = """
def all_valid_and_active(items):
    for item in items:
        if not item.is_valid() or not item.is_active():
            return False
    return True
"""
        detector = PipelinePatternDetector(code)
        matches = detector.detect_patterns()

        assert len(matches) == 1
        assert matches[0].pattern_type == PatternType.ALL_PATTERN


class TestAllPatternNoViolation:
    """Test cases that should NOT trigger all() pattern violations."""

    def test_no_violation_for_return_true_inside_loop(self) -> None:
        """Should not flag when return True is inside the loop (that's any())."""
        code = """
def check_items(items):
    for item in items:
        if item.is_valid():
            return True
    return False
"""
        detector = PipelinePatternDetector(code)
        matches = [
            m for m in detector.detect_patterns() if m.pattern_type == PatternType.ALL_PATTERN
        ]

        assert len(matches) == 0

    def test_no_violation_for_return_non_boolean(self) -> None:
        """Should not flag when return value is not True/False."""
        code = """
def find_invalid(items):
    for item in items:
        if not item.is_valid():
            return item
    return None
"""
        detector = PipelinePatternDetector(code)
        matches = [
            m for m in detector.detect_patterns() if m.pattern_type == PatternType.ALL_PATTERN
        ]

        assert len(matches) == 0

    def test_no_violation_for_missing_final_return(self) -> None:
        """Should not flag without return True after loop."""
        code = """
def check_items(items):
    for item in items:
        if not item.is_valid():
            return False
"""
        detector = PipelinePatternDetector(code)
        matches = [
            m for m in detector.detect_patterns() if m.pattern_type == PatternType.ALL_PATTERN
        ]

        assert len(matches) == 0

    def test_no_violation_for_for_else(self) -> None:
        """Should not flag for/else construct (different semantics)."""
        code = """
def check_items(items):
    for item in items:
        if not item.is_valid():
            return False
    else:
        log("All items valid")
    return True
"""
        detector = PipelinePatternDetector(code)
        matches = [
            m for m in detector.detect_patterns() if m.pattern_type == PatternType.ALL_PATTERN
        ]

        assert len(matches) == 0

    def test_no_violation_for_code_between_loop_and_return(self) -> None:
        """Should not flag when there's code between loop and return."""
        code = """
def check_items(items):
    for item in items:
        if not item.is_valid():
            return False
    log("All items checked")
    return True
"""
        detector = PipelinePatternDetector(code)
        matches = [
            m for m in detector.detect_patterns() if m.pattern_type == PatternType.ALL_PATTERN
        ]

        assert len(matches) == 0


class TestAllPatternEdgeCases:
    """Tests for edge cases in all() pattern detection."""

    def test_detects_in_method(self) -> None:
        """Detect all pattern inside class method."""
        code = """
class Validator:
    def all_valid(self, items):
        for item in items:
            if not item.is_valid():
                return False
        return True
"""
        detector = PipelinePatternDetector(code)
        matches = detector.detect_patterns()

        assert len(matches) == 1
        assert matches[0].pattern_type == PatternType.ALL_PATTERN

    def test_handles_multiple_functions_with_all_pattern(self) -> None:
        """Detect multiple all patterns in different functions."""
        code = """
def check_a(items):
    for item in items:
        if not item.valid:
            return False
    return True

def check_b(items):
    for item in items:
        if not item.special:
            return False
    return True
"""
        detector = PipelinePatternDetector(code)
        matches = [
            m for m in detector.detect_patterns() if m.pattern_type == PatternType.ALL_PATTERN
        ]

        assert len(matches) == 2


class TestAllPatternSuggestions:
    """Tests for all() pattern suggestion quality."""

    def test_suggestion_uses_all(self) -> None:
        """Suggestion should use all() builtin."""
        code = """
def all_valid(items):
    for item in items:
        if not item.is_valid():
            return False
    return True
"""
        detector = PipelinePatternDetector(code)
        matches = detector.detect_patterns()

        assert len(matches) == 1
        assert "all(" in matches[0].suggestion.lower()

    def test_suggestion_inverts_condition(self) -> None:
        """Suggestion should invert negated condition to positive."""
        code = """
def all_valid(items):
    for item in items:
        if not item.is_valid():
            return False
    return True
"""
        detector = PipelinePatternDetector(code)
        matches = detector.detect_patterns()

        assert len(matches) == 1
        # Condition should be inverted from "not item.is_valid()" to "item.is_valid()"
        suggestion = matches[0].suggestion
        assert "all(" in suggestion
        assert "item.is_valid()" in suggestion

    def test_suggestion_format(self) -> None:
        """Suggestion should have correct format: return all(cond for var in iter)."""
        code = """
def all_valid(items):
    for item in items:
        if not item.valid:
            return False
    return True
"""
        detector = PipelinePatternDetector(code)
        matches = detector.detect_patterns()

        assert len(matches) == 1
        suggestion = matches[0].suggestion
        assert "return all(" in suggestion
        assert "for item in items" in suggestion or "item in items" in suggestion

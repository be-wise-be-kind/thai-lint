"""
Purpose: Test detection of any() anti-patterns

Scope: Unit tests for detecting loops that should use any() builtin

Overview: Comprehensive test suite for detecting loops that return True on first match
    and False at the end, which can be refactored to any(). Tests cover basic patterns,
    edge cases, and false positive prevention. Follows TDD methodology.

Dependencies: pytest, src.linters.collection_pipeline.detector

Exports: TestAnyPatternBasic, TestAnyPatternEdgeCases, TestAnyPatternNoViolation

Interfaces: Standard pytest test classes with test methods

Implementation: TDD test cases for any() pattern detection
"""

from src.linters.collection_pipeline.detector import (
    PatternType,
    PipelinePatternDetector,
)


class TestAnyPatternBasic:
    """Tests for detection of basic any() patterns."""

    def test_detects_basic_any_pattern(self) -> None:
        """Detect: for x in iter: if cond(x): return True; return False."""
        code = """
def has_valid_item(items):
    for item in items:
        if item.is_valid():
            return True
    return False
"""
        detector = PipelinePatternDetector(code)
        matches = detector.detect_patterns()

        assert len(matches) == 1
        assert matches[0].pattern_type == PatternType.ANY_PATTERN
        assert matches[0].loop_var == "item"
        assert matches[0].iterable == "items"
        assert "any(" in matches[0].suggestion

    def test_detects_any_pattern_with_method_call(self) -> None:
        """Detect any pattern with method call condition."""
        code = """
def check_files(file_paths):
    for path in file_paths:
        if self._is_file_ignore_directive(path):
            return True
    return False
"""
        detector = PipelinePatternDetector(code)
        matches = detector.detect_patterns()

        assert len(matches) == 1
        assert matches[0].pattern_type == PatternType.ANY_PATTERN

    def test_detects_any_pattern_with_comparison(self) -> None:
        """Detect any pattern with comparison condition."""
        code = """
def has_large_number(numbers):
    for num in numbers:
        if num > 100:
            return True
    return False
"""
        detector = PipelinePatternDetector(code)
        matches = detector.detect_patterns()

        assert len(matches) == 1
        assert matches[0].pattern_type == PatternType.ANY_PATTERN
        assert "num > 100" in matches[0].suggestion or "any(" in matches[0].suggestion

    def test_detects_any_pattern_with_isinstance(self) -> None:
        """Detect any pattern with isinstance check."""
        code = """
def has_string(items):
    for item in items:
        if isinstance(item, str):
            return True
    return False
"""
        detector = PipelinePatternDetector(code)
        matches = detector.detect_patterns()

        assert len(matches) == 1
        assert matches[0].pattern_type == PatternType.ANY_PATTERN

    def test_detects_any_pattern_with_in_operator(self) -> None:
        """Detect any pattern with 'in' operator."""
        code = """
def contains_keyword(lines, keyword):
    for line in lines:
        if keyword in line:
            return True
    return False
"""
        detector = PipelinePatternDetector(code)
        matches = detector.detect_patterns()

        assert len(matches) == 1
        assert matches[0].pattern_type == PatternType.ANY_PATTERN


class TestAnyPatternCompoundConditions:
    """Tests for any() patterns with compound conditions."""

    def test_detects_any_pattern_with_and_condition(self) -> None:
        """Detect any pattern with 'and' compound condition."""
        code = """
def has_valid_large_item(items):
    for item in items:
        if item.is_valid() and item.size > 100:
            return True
    return False
"""
        detector = PipelinePatternDetector(code)
        matches = detector.detect_patterns()

        assert len(matches) == 1
        assert matches[0].pattern_type == PatternType.ANY_PATTERN

    def test_detects_any_pattern_with_or_condition(self) -> None:
        """Detect any pattern with 'or' compound condition."""
        code = """
def has_special_item(items):
    for item in items:
        if item.is_valid() or item.is_special():
            return True
    return False
"""
        detector = PipelinePatternDetector(code)
        matches = detector.detect_patterns()

        assert len(matches) == 1
        assert matches[0].pattern_type == PatternType.ANY_PATTERN


class TestAnyPatternNoViolation:
    """Test cases that should NOT trigger any() pattern violations."""

    def test_no_violation_for_return_false_inside_loop(self) -> None:
        """Should not flag when return False is inside the loop."""
        code = """
def check_items(items):
    for item in items:
        if item.is_invalid():
            return False
    return True
"""
        detector = PipelinePatternDetector(code)
        matches = [
            m for m in detector.detect_patterns() if m.pattern_type == PatternType.ANY_PATTERN
        ]

        assert len(matches) == 0

    def test_no_violation_for_return_non_boolean(self) -> None:
        """Should not flag when return value is not True/False."""
        code = """
def find_item(items):
    for item in items:
        if item.is_valid():
            return item
    return None
"""
        detector = PipelinePatternDetector(code)
        matches = [
            m for m in detector.detect_patterns() if m.pattern_type == PatternType.ANY_PATTERN
        ]

        assert len(matches) == 0

    def test_no_violation_for_missing_final_return(self) -> None:
        """Should not flag without return False after loop."""
        code = """
def check_items(items):
    for item in items:
        if item.is_valid():
            return True
"""
        detector = PipelinePatternDetector(code)
        matches = [
            m for m in detector.detect_patterns() if m.pattern_type == PatternType.ANY_PATTERN
        ]

        assert len(matches) == 0

    def test_no_violation_for_for_else(self) -> None:
        """Should not flag for/else construct (different semantics)."""
        code = """
def check_items(items):
    for item in items:
        if item.is_valid():
            return True
    else:
        log("No valid items found")
    return False
"""
        detector = PipelinePatternDetector(code)
        matches = [
            m for m in detector.detect_patterns() if m.pattern_type == PatternType.ANY_PATTERN
        ]

        assert len(matches) == 0

    def test_no_violation_for_code_between_loop_and_return(self) -> None:
        """Should not flag when there's code between loop and return."""
        code = """
def check_items(items):
    for item in items:
        if item.is_valid():
            return True
    log("Done checking")
    return False
"""
        detector = PipelinePatternDetector(code)
        matches = [
            m for m in detector.detect_patterns() if m.pattern_type == PatternType.ANY_PATTERN
        ]

        assert len(matches) == 0

    def test_no_violation_outside_function(self) -> None:
        """Should not flag any pattern at module level."""
        code = """
for item in items:
    if item.is_valid():
        break
"""
        detector = PipelinePatternDetector(code)
        matches = [
            m for m in detector.detect_patterns() if m.pattern_type == PatternType.ANY_PATTERN
        ]

        assert len(matches) == 0


class TestAnyPatternEdgeCases:
    """Tests for edge cases in any() pattern detection."""

    def test_detects_in_method(self) -> None:
        """Detect any pattern inside class method."""
        code = """
class Validator:
    def has_valid_item(self, items):
        for item in items:
            if item.is_valid():
                return True
        return False
"""
        detector = PipelinePatternDetector(code)
        matches = detector.detect_patterns()

        assert len(matches) == 1
        assert matches[0].pattern_type == PatternType.ANY_PATTERN

    def test_detects_in_nested_function(self) -> None:
        """Detect any pattern in nested function."""
        code = """
def outer():
    def inner(items):
        for item in items:
            if item.is_valid():
                return True
        return False
    return inner
"""
        detector = PipelinePatternDetector(code)
        matches = detector.detect_patterns()

        assert len(matches) == 1
        assert matches[0].pattern_type == PatternType.ANY_PATTERN

    def test_handles_multiple_functions_with_any_pattern(self) -> None:
        """Detect multiple any patterns in different functions."""
        code = """
def check_a(items):
    for item in items:
        if item.valid:
            return True
    return False

def check_b(items):
    for item in items:
        if item.special:
            return True
    return False
"""
        detector = PipelinePatternDetector(code)
        matches = [
            m for m in detector.detect_patterns() if m.pattern_type == PatternType.ANY_PATTERN
        ]

        assert len(matches) == 2


class TestAnyPatternSuggestions:
    """Tests for any() pattern suggestion quality."""

    def test_suggestion_uses_any(self) -> None:
        """Suggestion should use any() builtin."""
        code = """
def has_valid(items):
    for item in items:
        if item.is_valid():
            return True
    return False
"""
        detector = PipelinePatternDetector(code)
        matches = detector.detect_patterns()

        assert len(matches) == 1
        assert "any(" in matches[0].suggestion.lower()

    def test_suggestion_preserves_condition(self) -> None:
        """Suggestion should preserve the original condition."""
        code = """
def has_large(numbers):
    for n in numbers:
        if n > 100:
            return True
    return False
"""
        detector = PipelinePatternDetector(code)
        matches = detector.detect_patterns()

        assert len(matches) == 1
        assert "n > 100" in matches[0].suggestion or "> 100" in matches[0].suggestion

    def test_suggestion_format(self) -> None:
        """Suggestion should have correct format: return any(cond for var in iter)."""
        code = """
def has_valid(items):
    for item in items:
        if item.valid:
            return True
    return False
"""
        detector = PipelinePatternDetector(code)
        matches = detector.detect_patterns()

        assert len(matches) == 1
        suggestion = matches[0].suggestion
        assert "return any(" in suggestion
        assert "for item in items" in suggestion or "item in items" in suggestion

"""
Purpose: Test detection of takewhile anti-patterns

Scope: Unit tests for detecting loops that build lists until condition fails

Overview: Comprehensive test suite for detecting loops that initialize an empty list,
    iterate until a condition fails (break), then return the list. These can be
    refactored to itertools.takewhile(). Follows TDD methodology.

Dependencies: pytest, src.linters.collection_pipeline.detector

Exports: TestTakewhileBasic, TestTakewhileEdgeCases, TestTakewhileNoViolation

Interfaces: Standard pytest test classes with test methods

Implementation: TDD test cases for takewhile pattern detection
"""

from src.linters.collection_pipeline.detector import (
    PatternType,
    PipelinePatternDetector,
)


class TestTakewhileBasic:
    """Tests for detection of basic takewhile patterns."""

    def test_detects_basic_takewhile_pattern(self) -> None:
        """Detect: result=[]; for x: if not cond: break; result.append(x); return result."""
        code = """
def take_valid(items):
    results = []
    for item in items:
        if not item.is_valid():
            break
        results.append(item)
    return results
"""
        detector = PipelinePatternDetector(code)
        matches = detector.detect_patterns()

        assert len(matches) == 1
        assert matches[0].pattern_type == PatternType.TAKEWHILE
        assert matches[0].loop_var == "item"
        assert matches[0].iterable == "items"

    def test_detects_takewhile_with_positive_condition(self) -> None:
        """Detect takewhile with positive condition (if cond: break)."""
        code = """
def take_until_invalid(items):
    results = []
    for item in items:
        if item.is_invalid():
            break
        results.append(item)
    return results
"""
        detector = PipelinePatternDetector(code)
        matches = detector.detect_patterns()

        assert len(matches) == 1
        assert matches[0].pattern_type == PatternType.TAKEWHILE

    def test_detects_takewhile_with_comparison(self) -> None:
        """Detect takewhile with comparison condition."""
        code = """
def take_positive(numbers):
    results = []
    for num in numbers:
        if num <= 0:
            break
        results.append(num)
    return results
"""
        detector = PipelinePatternDetector(code)
        matches = detector.detect_patterns()

        assert len(matches) == 1
        assert matches[0].pattern_type == PatternType.TAKEWHILE

    def test_detects_takewhile_with_isinstance(self) -> None:
        """Detect takewhile with isinstance check."""
        code = """
def take_strings(items):
    results = []
    for item in items:
        if not isinstance(item, str):
            break
        results.append(item)
    return results
"""
        detector = PipelinePatternDetector(code)
        matches = detector.detect_patterns()

        assert len(matches) == 1
        assert matches[0].pattern_type == PatternType.TAKEWHILE


class TestTakewhileSuggestions:
    """Tests for takewhile suggestion quality."""

    def test_suggestion_uses_takewhile(self) -> None:
        """Suggestion should use itertools.takewhile()."""
        code = """
def take_valid(items):
    results = []
    for item in items:
        if not item.is_valid():
            break
        results.append(item)
    return results
"""
        detector = PipelinePatternDetector(code)
        matches = detector.detect_patterns()

        assert len(matches) == 1
        assert "takewhile" in matches[0].suggestion.lower()

    def test_suggestion_uses_lambda(self) -> None:
        """Suggestion should use lambda for condition."""
        code = """
def take_valid(items):
    results = []
    for item in items:
        if not item.is_valid():
            break
        results.append(item)
    return results
"""
        detector = PipelinePatternDetector(code)
        matches = detector.detect_patterns()

        assert len(matches) == 1
        assert "lambda" in matches[0].suggestion


class TestTakewhileNoViolation:
    """Test cases that should NOT trigger takewhile violations."""

    def test_no_violation_without_return(self) -> None:
        """Should not flag without return of the result list."""
        code = """
def process_items(items):
    results = []
    for item in items:
        if not item.is_valid():
            break
        results.append(item)
    # No return
"""
        detector = PipelinePatternDetector(code)
        matches = [m for m in detector.detect_patterns() if m.pattern_type == PatternType.TAKEWHILE]

        assert len(matches) == 0

    def test_no_violation_for_non_empty_list_init(self) -> None:
        """Should not flag when list is initialized with values."""
        code = """
def take_items(items):
    results = [first_item]
    for item in items:
        if not item.is_valid():
            break
        results.append(item)
    return results
"""
        detector = PipelinePatternDetector(code)
        matches = [m for m in detector.detect_patterns() if m.pattern_type == PatternType.TAKEWHILE]

        assert len(matches) == 0

    def test_no_violation_for_continue_instead_of_break(self) -> None:
        """Should not flag when using continue instead of break."""
        code = """
def filter_items(items):
    results = []
    for item in items:
        if not item.is_valid():
            continue
        results.append(item)
    return results
"""
        detector = PipelinePatternDetector(code)
        matches = [m for m in detector.detect_patterns() if m.pattern_type == PatternType.TAKEWHILE]

        # This is a filter pattern, not takewhile
        assert len(matches) == 0

    def test_no_violation_outside_function(self) -> None:
        """Should not flag takewhile at module level."""
        code = """
results = []
for item in items:
    if not item.is_valid():
        break
    results.append(item)
"""
        detector = PipelinePatternDetector(code)
        matches = [m for m in detector.detect_patterns() if m.pattern_type == PatternType.TAKEWHILE]

        assert len(matches) == 0


class TestTakewhileEdgeCases:
    """Tests for edge cases in takewhile detection."""

    def test_detects_in_method(self) -> None:
        """Detect takewhile inside class method."""
        code = """
class Processor:
    def take_valid(self, items):
        results = []
        for item in items:
            if not item.is_valid():
                break
            results.append(item)
        return results
"""
        detector = PipelinePatternDetector(code)
        matches = detector.detect_patterns()

        assert len(matches) == 1
        assert matches[0].pattern_type == PatternType.TAKEWHILE

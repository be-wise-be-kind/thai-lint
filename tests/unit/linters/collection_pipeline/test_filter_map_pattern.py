"""
Purpose: Test detection of filter-map anti-patterns

Scope: Unit tests for detecting loops that build lists with transform and filter

Overview: Comprehensive test suite for detecting loops that initialize an empty list,
    iterate with transform and conditional append, then return the list. These can be
    refactored to list comprehensions with walrus operator. Follows TDD methodology.

Dependencies: pytest, src.linters.collection_pipeline.detector

Exports: TestFilterMapBasic, TestFilterMapEdgeCases, TestFilterMapNoViolation

Interfaces: Standard pytest test classes with test methods

Implementation: TDD test cases for filter-map pattern detection
"""

from src.linters.collection_pipeline.detector import (
    PatternType,
    PipelinePatternDetector,
)


class TestFilterMapBasic:
    """Tests for detection of basic filter-map patterns."""

    def test_detects_basic_filter_map_pattern(self) -> None:
        """Detect: result=[]; for x: y=f(x); if y: result.append(y); return result."""
        code = """
def get_valid_results(items):
    results = []
    for item in items:
        result = process(item)
        if result:
            results.append(result)
    return results
"""
        detector = PipelinePatternDetector(code)
        matches = detector.detect_patterns()

        assert len(matches) == 1
        assert matches[0].pattern_type == PatternType.FILTER_MAP
        assert matches[0].loop_var == "item"
        assert matches[0].iterable == "items"

    def test_detects_filter_map_with_method_call(self) -> None:
        """Detect filter-map with method call transform."""
        code = """
def get_violations(matches, config, context):
    violations = []
    for match in matches:
        violation = self._process_match(match, config, context)
        if violation:
            violations.append(violation)
    return violations
"""
        detector = PipelinePatternDetector(code)
        matches = detector.detect_patterns()

        assert len(matches) == 1
        assert matches[0].pattern_type == PatternType.FILTER_MAP

    def test_detects_filter_map_with_type_annotation(self) -> None:
        """Detect filter-map with typed list initialization."""
        code = """
def get_violations(items):
    violations: list[Violation] = []
    for item in items:
        violation = validate(item)
        if violation:
            violations.append(violation)
    return violations
"""
        detector = PipelinePatternDetector(code)
        matches = detector.detect_patterns()

        assert len(matches) == 1
        assert matches[0].pattern_type == PatternType.FILTER_MAP


class TestFilterMapSuggestions:
    """Tests for filter-map suggestion quality."""

    def test_suggestion_uses_list_comprehension(self) -> None:
        """Suggestion should use list comprehension."""
        code = """
def get_results(items):
    results = []
    for item in items:
        result = process(item)
        if result:
            results.append(result)
    return results
"""
        detector = PipelinePatternDetector(code)
        matches = detector.detect_patterns()

        assert len(matches) == 1
        assert "[" in matches[0].suggestion and "]" in matches[0].suggestion
        assert "for" in matches[0].suggestion

    def test_suggestion_uses_walrus_operator(self) -> None:
        """Suggestion should use walrus operator by default."""
        code = """
def get_results(items):
    results = []
    for item in items:
        result = process(item)
        if result:
            results.append(result)
    return results
"""
        detector = PipelinePatternDetector(code)
        matches = detector.detect_patterns()

        assert len(matches) == 1
        assert ":=" in matches[0].suggestion


class TestFilterMapNoViolation:
    """Test cases that should NOT trigger filter-map violations."""

    def test_no_violation_without_return(self) -> None:
        """Should not flag without return of the result list."""
        code = """
def process_items(items):
    results = []
    for item in items:
        result = process(item)
        if result:
            results.append(result)
    # No return of results
"""
        detector = PipelinePatternDetector(code)
        matches = [
            m for m in detector.detect_patterns() if m.pattern_type == PatternType.FILTER_MAP
        ]

        assert len(matches) == 0

    def test_no_violation_for_different_variable_returned(self) -> None:
        """Should not flag when different variable is returned."""
        code = """
def process_items(items):
    results = []
    for item in items:
        result = process(item)
        if result:
            results.append(result)
    return other_list
"""
        detector = PipelinePatternDetector(code)
        matches = [
            m for m in detector.detect_patterns() if m.pattern_type == PatternType.FILTER_MAP
        ]

        assert len(matches) == 0

    def test_no_violation_for_non_empty_list_init(self) -> None:
        """Should not flag when list is initialized with values."""
        code = """
def process_items(items):
    results = [initial_value]
    for item in items:
        result = process(item)
        if result:
            results.append(result)
    return results
"""
        detector = PipelinePatternDetector(code)
        matches = [
            m for m in detector.detect_patterns() if m.pattern_type == PatternType.FILTER_MAP
        ]

        assert len(matches) == 0

    def test_no_violation_for_multiple_appends(self) -> None:
        """Should not flag when there are multiple appends."""
        code = """
def process_items(items):
    results = []
    for item in items:
        result = process(item)
        if result:
            results.append(result)
            results.append(result.extra)
    return results
"""
        detector = PipelinePatternDetector(code)
        matches = [
            m for m in detector.detect_patterns() if m.pattern_type == PatternType.FILTER_MAP
        ]

        assert len(matches) == 0

    def test_no_violation_without_conditional(self) -> None:
        """Should not flag simple map pattern without filter."""
        code = """
def process_items(items):
    results = []
    for item in items:
        result = process(item)
        results.append(result)
    return results
"""
        detector = PipelinePatternDetector(code)
        matches = [
            m for m in detector.detect_patterns() if m.pattern_type == PatternType.FILTER_MAP
        ]

        # This is a simple map pattern, not filter-map
        assert len(matches) == 0

    def test_no_violation_outside_function(self) -> None:
        """Should not flag filter-map at module level."""
        code = """
results = []
for item in items:
    result = process(item)
    if result:
        results.append(result)
"""
        detector = PipelinePatternDetector(code)
        matches = [
            m for m in detector.detect_patterns() if m.pattern_type == PatternType.FILTER_MAP
        ]

        assert len(matches) == 0


class TestFilterMapEdgeCases:
    """Tests for edge cases in filter-map detection."""

    def test_detects_in_method(self) -> None:
        """Detect filter-map inside class method."""
        code = """
class Processor:
    def get_results(self, items):
        results = []
        for item in items:
            result = self.process(item)
            if result:
                results.append(result)
        return results
"""
        detector = PipelinePatternDetector(code)
        matches = detector.detect_patterns()

        assert len(matches) == 1
        assert matches[0].pattern_type == PatternType.FILTER_MAP

    def test_handles_code_before_init(self) -> None:
        """Should handle code before list initialization."""
        code = """
def get_results(items):
    log("Starting")
    results = []
    for item in items:
        result = process(item)
        if result:
            results.append(result)
    return results
"""
        detector = PipelinePatternDetector(code)
        matches = detector.detect_patterns()

        assert len(matches) == 1
        assert matches[0].pattern_type == PatternType.FILTER_MAP

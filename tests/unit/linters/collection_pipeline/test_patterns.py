"""
Purpose: Test detection of collection pipeline anti-patterns

Scope: Unit tests for pattern matching logic in collection-pipeline linter

Overview: Comprehensive test suite for detecting embedded filtering patterns in for loops
    that could be refactored to collection pipelines. Tests cover single continue guards,
    multiple continue guards, and various false positive prevention cases. Follows TDD
    methodology with tests written before implementation.

Dependencies: pytest, src.linters.collection_pipeline.detector

Exports: TestSingleContinuePattern, TestMultipleContinuePattern, TestNoViolationCases

Interfaces: Standard pytest test classes with test methods

Implementation: TDD test cases covering pattern detection edge cases
"""

from src.linters.collection_pipeline.detector import PipelinePatternDetector


class TestSingleContinuePattern:
    """Tests for detection of single if/continue pattern."""

    def test_detects_if_not_continue(self) -> None:
        """Detect: for x in iter: if not cond: continue; action(x)."""
        code = """
for item in items:
    if not item.is_valid():
        continue
    process(item)
"""
        detector = PipelinePatternDetector(code)
        matches = detector.detect_patterns()

        assert len(matches) == 1
        assert matches[0].loop_var == "item"
        assert matches[0].iterable == "items"
        assert len(matches[0].conditions) == 1

    def test_detects_if_continue_positive_condition(self) -> None:
        """Detect: for x in iter: if cond: continue; action(x)."""
        code = """
for path in paths:
    if path.is_dir():
        continue
    lint_file(path)
"""
        detector = PipelinePatternDetector(code)
        matches = detector.detect_patterns()

        assert len(matches) == 1
        assert matches[0].loop_var == "path"

    def test_detects_glob_pattern(self) -> None:
        """Detect pattern with method call iterable."""
        code = """
for file_path in dir_path.glob(pattern):
    if not file_path.is_file():
        continue
    process(file_path)
"""
        detector = PipelinePatternDetector(code)
        matches = detector.detect_patterns()

        assert len(matches) == 1
        assert "glob" in matches[0].iterable


class TestMultipleContinuePattern:
    """Tests for detection of multiple if/continue patterns."""

    def test_detects_two_continues(self) -> None:
        """Detect: for x: if not c1: continue; if not c2: continue; action(x)."""
        code = """
for file_path in paths:
    if not file_path.is_file():
        continue
    if is_ignored(file_path):
        continue
    process(file_path)
"""
        detector = PipelinePatternDetector(code)
        matches = detector.detect_patterns()

        assert len(matches) == 1
        assert len(matches[0].conditions) == 2

    def test_detects_three_continues(self) -> None:
        """Detect three sequential if/continue patterns."""
        code = """
for item in items:
    if not cond1(item):
        continue
    if not cond2(item):
        continue
    if not cond3(item):
        continue
    process(item)
"""
        detector = PipelinePatternDetector(code)
        matches = detector.detect_patterns()

        assert len(matches) == 1
        assert len(matches[0].conditions) == 3


class TestNoViolationCases:
    """Test cases that should NOT trigger violations."""

    def test_no_violation_for_simple_loop(self) -> None:
        """Simple loop without filtering should not be flagged."""
        code = """
for item in items:
    process(item)
"""
        detector = PipelinePatternDetector(code)
        matches = detector.detect_patterns()

        assert len(matches) == 0

    def test_no_violation_for_loop_with_break(self) -> None:
        """Loop with break is not a filter pattern."""
        code = """
for item in items:
    if item.is_target():
        break
    process(item)
"""
        detector = PipelinePatternDetector(code)
        matches = detector.detect_patterns()

        assert len(matches) == 0

    def test_no_violation_for_loop_with_return(self) -> None:
        """Loop with return is handled by other rules (SIM110)."""
        code = """
for item in items:
    if item.matches():
        return item
"""
        detector = PipelinePatternDetector(code)
        matches = detector.detect_patterns()

        assert len(matches) == 0

    def test_no_violation_for_generator_expression(self) -> None:
        """Already using collection pipeline - no violation."""
        code = """
for item in (x for x in items if x.is_valid()):
    process(item)
"""
        detector = PipelinePatternDetector(code)
        matches = detector.detect_patterns()

        assert len(matches) == 0

    def test_no_violation_for_filter_builtin(self) -> None:
        """Already using filter() - no violation."""
        code = """
for item in filter(lambda x: x.is_valid(), items):
    process(item)
"""
        detector = PipelinePatternDetector(code)
        matches = detector.detect_patterns()

        assert len(matches) == 0

    def test_no_violation_for_if_with_else(self) -> None:
        """Don't flag if/continue when there's an else branch."""
        code = """
for item in items:
    if not item.is_valid():
        continue
    else:
        special_process(item)
    process(item)
"""
        detector = PipelinePatternDetector(code)
        matches = detector.detect_patterns()

        assert len(matches) == 0

    def test_no_violation_for_walrus_operator(self) -> None:
        """Don't flag if condition has side effects (walrus operator)."""
        code = """
for item in items:
    if not (result := validate(item)):
        continue
    process(item, result)
"""
        detector = PipelinePatternDetector(code)
        matches = detector.detect_patterns()

        assert len(matches) == 0

    def test_no_violation_for_empty_body_after_continue(self) -> None:
        """Don't flag if there's no body after continue guards."""
        code = """
for item in items:
    if not item.is_valid():
        continue
"""
        detector = PipelinePatternDetector(code)
        matches = detector.detect_patterns()

        assert len(matches) == 0


class TestEdgeCases:
    """Tests for edge cases and special scenarios."""

    def test_handles_empty_file(self) -> None:
        """Should handle empty files gracefully."""
        code = ""
        detector = PipelinePatternDetector(code)
        matches = detector.detect_patterns()

        assert len(matches) == 0

    def test_handles_syntax_error(self) -> None:
        """Should handle syntax errors gracefully."""
        code = "for x in items if"
        detector = PipelinePatternDetector(code)
        matches = detector.detect_patterns()

        assert len(matches) == 0

    def test_handles_unicode(self) -> None:
        """Should handle Unicode content correctly."""
        code = """
# Thai comment: สวัสดี
for item in items:
    if not item.valid:
        continue
    process(item)
"""
        detector = PipelinePatternDetector(code)
        matches = detector.detect_patterns()

        assert len(matches) == 1

    def test_detects_nested_loop_outer(self) -> None:
        """Should detect pattern in outer loop of nested loops."""
        code = """
for outer in outer_items:
    if not outer.valid:
        continue
    for inner in inner_items:
        process(outer, inner)
"""
        detector = PipelinePatternDetector(code)
        matches = detector.detect_patterns()

        assert len(matches) == 1
        assert matches[0].loop_var == "outer"

    def test_detects_pattern_in_function(self) -> None:
        """Should detect pattern inside function definition."""
        code = """
def process_items(items):
    for item in items:
        if not item.is_valid():
            continue
        do_something(item)
"""
        detector = PipelinePatternDetector(code)
        matches = detector.detect_patterns()

        assert len(matches) == 1

    def test_multiple_loops_detected(self) -> None:
        """Should detect patterns in multiple separate loops."""
        code = """
for item in items:
    if not item.valid:
        continue
    process1(item)

for other in others:
    if other.skip:
        continue
    process2(other)
"""
        detector = PipelinePatternDetector(code)
        matches = detector.detect_patterns()

        assert len(matches) == 2

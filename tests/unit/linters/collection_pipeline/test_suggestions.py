"""
Purpose: Test suggestion generation for collection pipeline refactoring

Scope: Unit tests for verifying accurate and helpful suggestions

Overview: Tests that the collection-pipeline linter generates correct refactoring
    suggestions. Verifies that suggestions include proper generator expression syntax,
    combined conditions, and correct variable naming.

Dependencies: pytest, src.linters.collection_pipeline.detector

Exports: TestSuggestions test class

Interfaces: Standard pytest test class with test methods

Implementation: TDD test cases for suggestion quality verification
"""

from src.linters.collection_pipeline.detector import PipelinePatternDetector


class TestSuggestions:
    """Tests for suggestion quality."""

    def test_suggests_generator_expression_single_condition(self) -> None:
        """Suggestion should show generator expression syntax for single condition."""
        code = """
for item in items:
    if not item.is_valid():
        continue
    process(item)
"""
        detector = PipelinePatternDetector(code)
        matches = detector.detect_patterns()

        assert len(matches) == 1
        suggestion = matches[0].suggestion
        assert "for item in" in suggestion
        assert "item.is_valid()" in suggestion

    def test_suggests_combined_conditions(self) -> None:
        """Multiple conditions should be combined with 'and'."""
        code = """
for path in paths:
    if not path.is_file():
        continue
    if is_ignored(path):
        continue
    process(path)
"""
        detector = PipelinePatternDetector(code)
        matches = detector.detect_patterns()

        assert len(matches) == 1
        suggestion = matches[0].suggestion
        assert "path.is_file()" in suggestion
        assert "not is_ignored(path)" in suggestion or "is_ignored(path)" in suggestion
        assert " and " in suggestion

    def test_inverts_negated_condition(self) -> None:
        """Should invert 'if not cond: continue' to positive condition."""
        code = """
for x in items:
    if not x:
        continue
    use(x)
"""
        detector = PipelinePatternDetector(code)
        matches = detector.detect_patterns()

        assert len(matches) == 1
        suggestion = matches[0].suggestion
        # The condition should be inverted from "not x" to "x"
        assert "if x" in suggestion or "for x in (x for x in items if x)" in suggestion

    def test_inverts_positive_condition(self) -> None:
        """Should invert 'if cond: continue' to negative condition."""
        code = """
for x in items:
    if x.skip:
        continue
    use(x)
"""
        detector = PipelinePatternDetector(code)
        matches = detector.detect_patterns()

        assert len(matches) == 1
        suggestion = matches[0].suggestion
        # The condition should be inverted from "x.skip" to "not x.skip"
        assert "not" in suggestion

    def test_preserves_method_call_in_condition(self) -> None:
        """Should preserve method calls in conditions."""
        code = """
for path in paths:
    if not path.exists():
        continue
    read(path)
"""
        detector = PipelinePatternDetector(code)
        matches = detector.detect_patterns()

        assert len(matches) == 1
        suggestion = matches[0].suggestion
        assert "path.exists()" in suggestion

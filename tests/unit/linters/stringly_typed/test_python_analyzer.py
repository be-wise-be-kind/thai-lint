"""
Purpose: Tests for Python stringly-typed analyzer coordination

Scope: Unit tests for PythonStringlyTypedAnalyzer class

Overview: Comprehensive test suite for PythonStringlyTypedAnalyzer verifying correct
    coordination of pattern detection, configuration handling, and result conversion.
    Tests cover analysis of various Python code samples, syntax error handling,
    configuration options, and unified result format.

Dependencies: pytest, pathlib

Exports: Test functions for Python analyzer

Interfaces: pytest test discovery

Implementation: pytest fixtures with sample code, parametrized tests for coverage
"""

from pathlib import Path

from src.linters.stringly_typed.config import StringlyTypedConfig
from src.linters.stringly_typed.python.analyzer import (
    AnalysisResult,
    PythonStringlyTypedAnalyzer,
)


class TestPythonStringlyTypedAnalyzerBasic:
    """Tests for basic analyzer functionality."""

    def test_analyze_returns_empty_for_no_patterns(self) -> None:
        """Return empty list when no patterns found."""
        code = """
def simple_function(x: int) -> int:
    return x + 1
"""
        analyzer = PythonStringlyTypedAnalyzer()
        results = analyzer.analyze(code, Path("test.py"))

        assert results == []

    def test_analyze_detects_membership_pattern(self) -> None:
        """Detect membership validation pattern."""
        code = """
def validate(x: str) -> bool:
    return x in ("staging", "production")
"""
        analyzer = PythonStringlyTypedAnalyzer()
        results = analyzer.analyze(code, Path("test.py"))

        assert len(results) == 1
        assert results[0].pattern_type == "membership_validation"
        assert results[0].string_values == {"staging", "production"}

    def test_analyze_returns_correct_file_path(self) -> None:
        """Return correct file path in results."""
        code = """
def check(x: str) -> bool:
    return x in ("a", "b")
"""
        file_path = Path("/project/src/validator.py")
        analyzer = PythonStringlyTypedAnalyzer()
        results = analyzer.analyze(code, file_path)

        assert len(results) == 1
        assert results[0].file_path == file_path


class TestPythonStringlyTypedAnalyzerErrorHandling:
    """Tests for error handling in analyzer."""

    def test_handles_syntax_error_gracefully(self) -> None:
        """Return empty list for code with syntax errors."""
        code = """
def broken(x: str -> bool:
    return x
"""
        analyzer = PythonStringlyTypedAnalyzer()
        results = analyzer.analyze(code, Path("broken.py"))

        assert results == []

    def test_handles_empty_code(self) -> None:
        """Handle empty code input."""
        analyzer = PythonStringlyTypedAnalyzer()
        results = analyzer.analyze("", Path("empty.py"))

        assert results == []


class TestPythonStringlyTypedAnalyzerConfig:
    """Tests for configuration handling."""

    def test_uses_default_config_when_none_provided(self) -> None:
        """Use default config when none provided."""
        analyzer = PythonStringlyTypedAnalyzer()

        assert analyzer.config is not None
        assert analyzer.config.enabled is True
        assert analyzer.config.min_occurrences == 2

    def test_uses_provided_config(self) -> None:
        """Use provided config."""
        config = StringlyTypedConfig(
            min_occurrences=5,
            min_values_for_enum=3,
        )
        analyzer = PythonStringlyTypedAnalyzer(config=config)

        assert analyzer.config.min_occurrences == 5
        assert analyzer.config.min_values_for_enum == 3


class TestAnalysisResultDataclass:
    """Tests for AnalysisResult dataclass."""

    def test_result_has_all_required_fields(self) -> None:
        """Verify AnalysisResult has all required fields."""
        result = AnalysisResult(
            pattern_type="membership_validation",
            string_values={"a", "b"},
            file_path=Path("test.py"),
            line_number=10,
            column=4,
            variable_name="status",
            details="Test details",
        )

        assert result.pattern_type == "membership_validation"
        assert result.string_values == {"a", "b"}
        assert result.file_path == Path("test.py")
        assert result.line_number == 10
        assert result.column == 4
        assert result.variable_name == "status"
        assert result.details == "Test details"

    def test_result_variable_name_can_be_none(self) -> None:
        """Verify variable_name can be None."""
        result = AnalysisResult(
            pattern_type="membership_validation",
            string_values={"a", "b"},
            file_path=Path("test.py"),
            line_number=10,
            column=4,
            variable_name=None,
            details="Test details",
        )

        assert result.variable_name is None


class TestAnalysisResultDetails:
    """Tests for AnalysisResult details field generation."""

    def test_details_include_value_count(self) -> None:
        """Verify details include count of string values."""
        code = """
def check(x: str) -> bool:
    return x in ("a", "b", "c")
"""
        analyzer = PythonStringlyTypedAnalyzer()
        results = analyzer.analyze(code, Path("test.py"))

        assert len(results) == 1
        assert "3 string values" in results[0].details

    def test_details_include_variable_name_when_present(self) -> None:
        """Verify details include variable name when present."""
        code = """
def check(status: str) -> bool:
    return status in ("a", "b")
"""
        analyzer = PythonStringlyTypedAnalyzer()
        results = analyzer.analyze(code, Path("test.py"))

        assert len(results) == 1
        assert "'status'" in results[0].details

    def test_details_include_operator(self) -> None:
        """Verify details include operator used."""
        code = """
def check(x: str) -> bool:
    return x not in ("a", "b")
"""
        analyzer = PythonStringlyTypedAnalyzer()
        results = analyzer.analyze(code, Path("test.py"))

        assert len(results) == 1
        assert "(not in)" in results[0].details


class TestMultiplePatterns:
    """Tests for multiple patterns in same file."""

    def test_detects_multiple_membership_patterns(self) -> None:
        """Detect multiple membership patterns in same file."""
        code = """
def validate_all(env: str, status: str) -> bool:
    if env not in ("dev", "prod"):
        return False
    if status in {"pending", "completed"}:
        return True
    return False
"""
        analyzer = PythonStringlyTypedAnalyzer()
        results = analyzer.analyze(code, Path("test.py"))

        assert len(results) == 2
        pattern_types = {r.pattern_type for r in results}
        assert pattern_types == {"membership_validation"}

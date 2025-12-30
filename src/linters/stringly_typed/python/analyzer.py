"""
Purpose: Coordinate Python stringly-typed pattern detection

Scope: Orchestrate detection of all stringly-typed patterns in Python files

Overview: Provides PythonStringlyTypedAnalyzer class that coordinates detection of
    stringly-typed patterns across Python source files. Uses MembershipValidationDetector
    to find 'x in ("a", "b")' patterns, ConditionalPatternDetector to find if/elif chains
    and match statements, and FunctionCallTracker to find function calls with string
    arguments. Returns unified AnalysisResult objects for validation patterns and
    FunctionCallResult objects for function calls. Handles AST parsing errors gracefully
    and provides a single entry point for Python analysis. Supports configuration options
    for filtering and thresholds.

Dependencies: ast module, MembershipValidationDetector, ConditionalPatternDetector,
    FunctionCallTracker, StringlyTypedConfig

Exports: PythonStringlyTypedAnalyzer class, AnalysisResult dataclass, FunctionCallResult dataclass,
    ComparisonResult dataclass

Interfaces: PythonStringlyTypedAnalyzer.analyze(code, file_path) -> list[AnalysisResult],
    PythonStringlyTypedAnalyzer.analyze_function_calls(code, file_path) -> list[FunctionCallResult]

Implementation: Facade pattern coordinating multiple detectors with unified result format

Suppressions:
    - srp: Analyzer coordinates multiple detectors (membership, conditional, call tracker).
        Facade pattern justifies combining orchestration methods.
"""

import ast
from dataclasses import dataclass
from pathlib import Path

from ..config import StringlyTypedConfig
from .call_tracker import FunctionCallPattern, FunctionCallTracker
from .comparison_tracker import ComparisonPattern, ComparisonTracker
from .conditional_detector import ConditionalPatternDetector, EqualityChainPattern
from .validation_detector import MembershipPattern, MembershipValidationDetector


@dataclass
class AnalysisResult:
    """Represents a stringly-typed pattern detected in Python code.

    Provides a unified representation of detected patterns from all detectors,
    including pattern type, string values, location, and contextual information.
    """

    pattern_type: str
    """Type of pattern detected: 'membership_validation', 'equality_chain', etc."""

    string_values: set[str]
    """Set of string values used in the pattern."""

    file_path: Path
    """Path to the file containing the pattern."""

    line_number: int
    """Line number where the pattern occurs (1-indexed)."""

    column: int
    """Column number where the pattern starts (0-indexed)."""

    variable_name: str | None
    """Variable name involved in the pattern, if identifiable."""

    details: str
    """Human-readable description of the detected pattern."""


@dataclass
class FunctionCallResult:
    """Represents a function call with a string argument.

    Provides information about a single function call with a string literal
    argument, enabling aggregation across files to detect limited value sets.
    """

    function_name: str
    """Fully qualified function name (e.g., 'process' or 'obj.method')."""

    param_index: int
    """Index of the parameter receiving the string value (0-indexed)."""

    string_value: str
    """The string literal value passed to the function."""

    file_path: Path
    """Path to the file containing the call."""

    line_number: int
    """Line number where the call occurs (1-indexed)."""

    column: int
    """Column number where the call starts (0-indexed)."""


@dataclass
class ComparisonResult:
    """Represents a string comparison found in Python code.

    Provides information about a comparison like `if env == "production"` to
    enable cross-file aggregation for detecting scattered comparisons that
    suggest missing enums.
    """

    variable_name: str
    """Variable name being compared (e.g., 'env' or 'self.status')."""

    compared_value: str
    """The string literal value being compared to."""

    operator: str
    """The comparison operator ('==' or '!=')."""

    file_path: Path
    """Path to the file containing the comparison."""

    line_number: int
    """Line number where the comparison occurs (1-indexed)."""

    column: int
    """Column number where the comparison starts (0-indexed)."""


class PythonStringlyTypedAnalyzer:  # thailint: ignore[srp]
    """Analyzes Python code for stringly-typed patterns.

    Coordinates detection of various stringly-typed patterns including membership
    validation ('x in ("a", "b")'), equality chains ('if x == "a" elif x == "b"'),
    and function calls with string arguments ('process("active")').
    Provides configuration-aware analysis with filtering support.

    Note: Method count exceeds SRP limit due to analyzer coordination role. Multiple
    analysis methods are required for different pattern types (membership, conditional,
    function calls, comparisons) and their converters.
    """

    def __init__(self, config: StringlyTypedConfig | None = None) -> None:
        """Initialize the analyzer with optional configuration.

        Args:
            config: Configuration for stringly-typed detection. Uses defaults if None.
        """
        self.config = config or StringlyTypedConfig()
        self._membership_detector = MembershipValidationDetector()
        self._conditional_detector = ConditionalPatternDetector()
        self._call_tracker = FunctionCallTracker()
        self._comparison_tracker = ComparisonTracker()

    def analyze(self, code: str, file_path: Path) -> list[AnalysisResult]:
        """Analyze Python code for stringly-typed patterns.

        Args:
            code: Python source code to analyze
            file_path: Path to the file being analyzed

        Returns:
            List of AnalysisResult instances for each detected pattern
        """
        tree = self._parse_code(code)
        if tree is None:
            return []

        results: list[AnalysisResult] = []

        # Detect membership validation patterns
        membership_patterns = self._membership_detector.find_patterns(tree)
        results.extend(
            self._convert_membership_pattern(pattern, file_path) for pattern in membership_patterns
        )

        # Detect equality chain patterns
        conditional_patterns = self._conditional_detector.find_patterns(tree)
        results.extend(
            self._convert_conditional_pattern(pattern, file_path)
            for pattern in conditional_patterns
        )

        return results

    def _parse_code(self, code: str) -> ast.AST | None:
        """Parse Python source code into an AST.

        Args:
            code: Python source code to parse

        Returns:
            AST if parsing succeeds, None if parsing fails
        """
        try:
            return ast.parse(code)
        except SyntaxError:
            return None

    def _convert_membership_pattern(
        self, pattern: MembershipPattern, file_path: Path
    ) -> AnalysisResult:
        """Convert a MembershipPattern to unified AnalysisResult.

        Args:
            pattern: Detected membership pattern
            file_path: Path to the file containing the pattern

        Returns:
            AnalysisResult representing the pattern
        """
        values_str = ", ".join(sorted(pattern.string_values))
        var_info = f" on '{pattern.variable_name}'" if pattern.variable_name else ""
        details = (
            f"Membership validation{var_info} with {len(pattern.string_values)} "
            f"string values ({pattern.operator}): {values_str}"
        )

        return AnalysisResult(
            pattern_type="membership_validation",
            string_values=pattern.string_values,
            file_path=file_path,
            line_number=pattern.line_number,
            column=pattern.column,
            variable_name=pattern.variable_name,
            details=details,
        )

    def _convert_conditional_pattern(
        self, pattern: EqualityChainPattern, file_path: Path
    ) -> AnalysisResult:
        """Convert an EqualityChainPattern to unified AnalysisResult.

        Args:
            pattern: Detected equality chain pattern
            file_path: Path to the file containing the pattern

        Returns:
            AnalysisResult representing the pattern
        """
        values_str = ", ".join(sorted(pattern.string_values))
        var_info = f" on '{pattern.variable_name}'" if pattern.variable_name else ""
        pattern_label = self._get_pattern_label(pattern.pattern_type)
        details = (
            f"{pattern_label}{var_info} with {len(pattern.string_values)} "
            f"string values: {values_str}"
        )

        return AnalysisResult(
            pattern_type=pattern.pattern_type,
            string_values=pattern.string_values,
            file_path=file_path,
            line_number=pattern.line_number,
            column=pattern.column,
            variable_name=pattern.variable_name,
            details=details,
        )

    def _get_pattern_label(self, pattern_type: str) -> str:
        """Get human-readable label for a pattern type.

        Args:
            pattern_type: The pattern type string

        Returns:
            Human-readable label for the pattern
        """
        labels = {
            "equality_chain": "Equality chain",
            "or_combined": "Or-combined comparison",
            "match_statement": "Match statement",
        }
        return labels.get(pattern_type, "Conditional pattern")

    def analyze_function_calls(self, code: str, file_path: Path) -> list[FunctionCallResult]:
        """Analyze Python code for function calls with string arguments.

        Args:
            code: Python source code to analyze
            file_path: Path to the file being analyzed

        Returns:
            List of FunctionCallResult instances for each detected call
        """
        tree = self._parse_code(code)
        if tree is None:
            return []

        call_patterns = self._call_tracker.find_patterns(tree)
        return [self._convert_call_pattern(pattern, file_path) for pattern in call_patterns]

    def _convert_call_pattern(
        self, pattern: FunctionCallPattern, file_path: Path
    ) -> FunctionCallResult:
        """Convert a FunctionCallPattern to FunctionCallResult.

        Args:
            pattern: Detected function call pattern
            file_path: Path to the file containing the call

        Returns:
            FunctionCallResult representing the call
        """
        return FunctionCallResult(
            function_name=pattern.function_name,
            param_index=pattern.param_index,
            string_value=pattern.string_value,
            file_path=file_path,
            line_number=pattern.line_number,
            column=pattern.column,
        )

    def analyze_comparisons(self, code: str, file_path: Path) -> list[ComparisonResult]:
        """Analyze Python code for string comparisons.

        Args:
            code: Python source code to analyze
            file_path: Path to the file being analyzed

        Returns:
            List of ComparisonResult instances for each detected comparison
        """
        tree = self._parse_code(code)
        if tree is None:
            return []

        comparison_patterns = self._comparison_tracker.find_patterns(tree)
        return [
            self._convert_comparison_pattern(pattern, file_path) for pattern in comparison_patterns
        ]

    def _convert_comparison_pattern(
        self, pattern: ComparisonPattern, file_path: Path
    ) -> ComparisonResult:
        """Convert a ComparisonPattern to ComparisonResult.

        Args:
            pattern: Detected comparison pattern
            file_path: Path to the file containing the comparison

        Returns:
            ComparisonResult representing the comparison
        """
        return ComparisonResult(
            variable_name=pattern.variable_name,
            compared_value=pattern.compared_value,
            operator=pattern.operator,
            file_path=file_path,
            line_number=pattern.line_number,
            column=pattern.column,
        )

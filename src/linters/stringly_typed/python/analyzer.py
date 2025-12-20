"""
Purpose: Coordinate Python stringly-typed pattern detection

Scope: Orchestrate detection of all stringly-typed patterns in Python files

Overview: Provides PythonStringlyTypedAnalyzer class that coordinates detection of
    stringly-typed patterns across Python source files. Uses MembershipValidationDetector
    to find 'x in ("a", "b")' patterns and returns unified AnalysisResult objects. Handles
    AST parsing errors gracefully and provides a single entry point for Python analysis.
    Supports configuration options for filtering and thresholds.

Dependencies: ast module, MembershipValidationDetector, StringlyTypedConfig

Exports: PythonStringlyTypedAnalyzer class, AnalysisResult dataclass

Interfaces: PythonStringlyTypedAnalyzer.analyze(code, file_path) -> list[AnalysisResult]

Implementation: Facade pattern coordinating multiple detectors with unified result format
"""

import ast
from dataclasses import dataclass
from pathlib import Path

from ..config import StringlyTypedConfig
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


class PythonStringlyTypedAnalyzer:
    """Analyzes Python code for stringly-typed patterns.

    Coordinates detection of various stringly-typed patterns including membership
    validation ('x in ("a", "b")') and equality chains ('if x == "a" elif x == "b"').
    Provides configuration-aware analysis with filtering support.
    """

    def __init__(self, config: StringlyTypedConfig | None = None) -> None:
        """Initialize the analyzer with optional configuration.

        Args:
            config: Configuration for stringly-typed detection. Uses defaults if None.
        """
        self.config = config or StringlyTypedConfig()
        self._membership_detector = MembershipValidationDetector()

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

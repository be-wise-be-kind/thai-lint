"""
Purpose: Coordinate TypeScript stringly-typed pattern detection

Scope: Orchestrate detection of stringly-typed patterns in TypeScript and JavaScript files

Overview: Provides TypeScriptStringlyTypedAnalyzer class that coordinates detection of
    stringly-typed patterns across TypeScript and JavaScript source files. Uses
    TypeScriptCallTracker to find function calls with string arguments and
    TypeScriptComparisonTracker to find scattered string comparisons. Returns
    FunctionCallResult and ComparisonResult objects compatible with the Python analyzer
    format for unified cross-file analysis. Handles tree-sitter parsing gracefully and
    provides a single entry point for TypeScript analysis. Supports configuration options
    for filtering and thresholds.

Dependencies: TypeScriptCallTracker, TypeScriptComparisonTracker, StringlyTypedConfig,
    pathlib.Path

Exports: TypeScriptStringlyTypedAnalyzer class, FunctionCallResult (re-export from Python),
    ComparisonResult (re-export from Python)

Interfaces: TypeScriptStringlyTypedAnalyzer.analyze_function_calls(code, file_path)
    -> list[FunctionCallResult], TypeScriptStringlyTypedAnalyzer.analyze_comparisons(code,
    file_path) -> list[ComparisonResult]

Implementation: Facade pattern coordinating TypeScript-specific detectors with unified result format
"""

from pathlib import Path

from ..config import StringlyTypedConfig
from ..python.analyzer import ComparisonResult, FunctionCallResult
from .call_tracker import TypeScriptCallTracker, TypeScriptFunctionCallPattern
from .comparison_tracker import TypeScriptComparisonPattern, TypeScriptComparisonTracker


class TypeScriptStringlyTypedAnalyzer:
    """Analyzes TypeScript/JavaScript code for stringly-typed patterns.

    Coordinates detection of stringly-typed patterns including function calls
    with string arguments ('process("active")', 'obj.setStatus("pending")') and
    scattered string comparisons ('if (env === "production")').
    Provides configuration-aware analysis with filtering support.
    """

    def __init__(self, config: StringlyTypedConfig | None = None) -> None:
        """Initialize the analyzer with optional configuration.

        Args:
            config: Configuration for stringly-typed detection. Uses defaults if None.
        """
        self.config = config or StringlyTypedConfig()
        self._call_tracker = TypeScriptCallTracker()
        self._comparison_tracker = TypeScriptComparisonTracker()

    def analyze_function_calls(self, code: str, file_path: Path) -> list[FunctionCallResult]:
        """Analyze TypeScript code for function calls with string arguments.

        Args:
            code: TypeScript source code to analyze
            file_path: Path to the file being analyzed

        Returns:
            List of FunctionCallResult instances for each detected call
        """
        call_patterns = self._call_tracker.find_patterns(code)
        return [self._convert_call_pattern(pattern, file_path) for pattern in call_patterns]

    def _convert_call_pattern(
        self, pattern: TypeScriptFunctionCallPattern, file_path: Path
    ) -> FunctionCallResult:
        """Convert a TypeScriptFunctionCallPattern to FunctionCallResult.

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
        """Analyze TypeScript code for string comparisons.

        Args:
            code: TypeScript source code to analyze
            file_path: Path to the file being analyzed

        Returns:
            List of ComparisonResult instances for each detected comparison
        """
        comparison_patterns = self._comparison_tracker.find_patterns(code)
        return [
            self._convert_comparison_pattern(pattern, file_path) for pattern in comparison_patterns
        ]

    def _convert_comparison_pattern(
        self, pattern: TypeScriptComparisonPattern, file_path: Path
    ) -> ComparisonResult:
        """Convert a TypeScriptComparisonPattern to ComparisonResult.

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

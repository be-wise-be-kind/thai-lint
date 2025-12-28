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
    pathlib.Path, TypeScriptBaseAnalyzer

Exports: TypeScriptStringlyTypedAnalyzer class, FunctionCallResult (re-export from Python),
    ComparisonResult (re-export from Python)

Interfaces: TypeScriptStringlyTypedAnalyzer.analyze_all(code, file_path) for optimized
    single-parse analysis, plus individual analyze_function_calls and analyze_comparisons

Implementation: Facade pattern with single-parse optimization for performance
"""

from pathlib import Path

from src.analyzers.typescript_base import TypeScriptBaseAnalyzer

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

    Uses single-parse optimization: parses code once and passes AST to both trackers.
    """

    def __init__(self, config: StringlyTypedConfig | None = None) -> None:
        """Initialize the analyzer with optional configuration.

        Args:
            config: Configuration for stringly-typed detection. Uses defaults if None.
        """
        self.config = config or StringlyTypedConfig()
        self._call_tracker = TypeScriptCallTracker()
        self._comparison_tracker = TypeScriptComparisonTracker()
        self._base_analyzer = TypeScriptBaseAnalyzer()

    def analyze_all(
        self, code: str, file_path: Path
    ) -> tuple[list[FunctionCallResult], list[ComparisonResult]]:
        """Analyze TypeScript code for all stringly-typed patterns in single parse.

        Optimized method that parses the code once and runs both call and comparison
        detection on the same AST tree, avoiding duplicate parsing overhead.

        Args:
            code: TypeScript source code to analyze
            file_path: Path to the file being analyzed

        Returns:
            Tuple of (function_call_results, comparison_results)
        """
        # Parse once
        tree = self._base_analyzer.parse_typescript(code)
        if tree is None:
            return [], []

        # Run both trackers with pre-parsed tree
        call_patterns = self._call_tracker.find_patterns_from_tree(tree)
        comp_patterns = self._comparison_tracker.find_patterns_from_tree(tree)

        # Convert to result objects
        calls = [self._convert_call_pattern(p, file_path) for p in call_patterns]
        comps = [self._convert_comparison_pattern(p, file_path) for p in comp_patterns]

        return calls, comps

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

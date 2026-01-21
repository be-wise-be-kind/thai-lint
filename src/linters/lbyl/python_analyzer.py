"""
Purpose: Coordinate LBYL pattern detection and violation generation

Scope: Orchestrates multiple pattern detectors and converts results to violations

Overview: Provides PythonLBYLAnalyzer class that coordinates all LBYL pattern detectors
    and converts detected patterns into Violation objects. Handles AST parsing with
    graceful syntax error handling, runs enabled detectors based on configuration toggles,
    and aggregates violations from all detectors. Serves as the main analysis engine
    called by LBYLRule.

Dependencies: ast module, LBYLConfig, pattern detectors, violation_builder functions

Exports: PythonLBYLAnalyzer

Interfaces: analyze(code: str, file_path: str, config: LBYLConfig) -> list[Violation]

Implementation: Detector coordination with config-driven pattern selection
"""

import ast

from src.core.types import Violation

from .config import LBYLConfig
from .pattern_detectors.dict_key_detector import DictKeyDetector, DictKeyPattern
from .violation_builder import build_dict_key_violation


class PythonLBYLAnalyzer:
    """Coordinates LBYL pattern detection for Python code."""

    def __init__(self) -> None:
        """Initialize the analyzer with pattern detectors."""
        self._dict_key_detector = DictKeyDetector()

    def analyze(self, code: str, file_path: str, config: LBYLConfig) -> list[Violation]:
        """Analyze Python code for LBYL patterns.

        Args:
            code: Python source code to analyze
            file_path: Path to the file being analyzed
            config: LBYL configuration with pattern toggles

        Returns:
            List of violations for detected LBYL patterns
        """
        if not code or not code.strip():
            return []

        tree = self._parse_ast(code)
        if tree is None:
            return []

        violations: list[Violation] = []

        if config.detect_dict_key:
            violations.extend(self._detect_dict_key_patterns(tree, file_path))

        return violations

    def _parse_ast(self, code: str) -> ast.Module | None:
        """Parse Python code into AST."""
        try:
            return ast.parse(code)
        except SyntaxError:
            return None

    def _detect_dict_key_patterns(self, tree: ast.Module, file_path: str) -> list[Violation]:
        """Detect dict key LBYL patterns and convert to violations."""
        violations: list[Violation] = []
        patterns = self._dict_key_detector.find_patterns(tree)

        for pattern in patterns:
            if isinstance(pattern, DictKeyPattern):
                violation = build_dict_key_violation(
                    file_path=file_path,
                    line=pattern.line_number,
                    column=pattern.column,
                    dict_name=pattern.dict_name,
                    key_expression=pattern.key_expression,
                )
                violations.append(violation)

        return violations

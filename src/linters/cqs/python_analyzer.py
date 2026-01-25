"""
Purpose: Coordinator for Python CQS analysis combining INPUT and OUTPUT detection

Scope: High-level analyzer that orchestrates detection and handles parsing

Overview: Provides PythonCQSAnalyzer class that coordinates InputDetector and OutputDetector
    to analyze Python code for CQS patterns. Handles AST parsing with proper SyntaxError
    handling, returning empty results for unparseable code rather than raising exceptions.
    Returns raw INPUT and OUTPUT operations for further analysis. PR3 will build on this
    to aggregate operations per function and detect CQS violations.

Dependencies: ast module, InputDetector, OutputDetector, CQSConfig

Exports: PythonCQSAnalyzer

Interfaces: PythonCQSAnalyzer.analyze(code, file_path, config) -> (inputs, outputs)

Implementation: Coordinates detectors with error handling for AST parsing failures
"""

import ast

from .config import CQSConfig
from .input_detector import InputDetector
from .output_detector import OutputDetector
from .types import InputOperation, OutputOperation


class PythonCQSAnalyzer:
    """Analyzes Python code for CQS INPUT and OUTPUT operations."""

    def __init__(self) -> None:
        """Initialize the analyzer with detectors."""
        self._input_detector = InputDetector()
        self._output_detector = OutputDetector()

    def analyze(
        self,
        code: str,
        file_path: str,
        config: CQSConfig,
    ) -> tuple[list[InputOperation], list[OutputOperation]]:
        """Analyze Python code for INPUT and OUTPUT operations.

        Args:
            code: Python source code to analyze
            file_path: Path to the source file (for error context)
            config: CQS configuration settings

        Returns:
            Tuple of (inputs, outputs) lists. Returns empty lists if code
            cannot be parsed due to SyntaxError.
        """
        # Config parameter reserved for PR3 filtering logic
        _ = config

        try:
            tree = ast.parse(code, filename=file_path)
        except SyntaxError:
            return [], []

        inputs = self._input_detector.find_inputs(tree)
        outputs = self._output_detector.find_outputs(tree)

        return inputs, outputs

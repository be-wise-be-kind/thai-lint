"""
Purpose: Coordinator for Python CQS analysis returning per-function CQSPattern objects

Scope: High-level analyzer that orchestrates FunctionAnalyzer for function-level detection

Overview: Provides PythonCQSAnalyzer class that coordinates CQS pattern detection in Python
    code. Handles AST parsing with proper SyntaxError handling, returning empty results for
    unparseable code rather than raising exceptions. Delegates to FunctionAnalyzer to build
    CQSPattern objects for each function/method, which contain INPUT and OUTPUT operations
    along with function metadata (name, class context, async status).

Dependencies: ast module, FunctionAnalyzer, CQSConfig, CQSPattern

Exports: PythonCQSAnalyzer

Interfaces: PythonCQSAnalyzer.analyze(code, file_path, config) -> list[CQSPattern]

Implementation: Coordinates FunctionAnalyzer with error handling for AST parsing failures
"""

import ast

from .config import CQSConfig
from .function_analyzer import FunctionAnalyzer
from .types import CQSPattern


class PythonCQSAnalyzer:
    """Analyzes Python code for CQS patterns, returning per-function results."""

    def analyze(
        self,
        code: str,
        file_path: str,
        config: CQSConfig,
    ) -> list[CQSPattern]:
        """Analyze Python code for CQS patterns in each function.

        Args:
            code: Python source code to analyze
            file_path: Path to the source file (for error context)
            config: CQS configuration settings

        Returns:
            List of CQSPattern objects, one per function/method.
            Returns empty list if code cannot be parsed due to SyntaxError.
        """
        try:
            tree = ast.parse(code, filename=file_path)
        except SyntaxError:
            return []

        analyzer = FunctionAnalyzer(file_path, config)
        return analyzer.analyze(tree)

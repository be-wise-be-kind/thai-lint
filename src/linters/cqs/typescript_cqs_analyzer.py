"""
Purpose: Coordinator for TypeScript CQS analysis returning per-function CQSPattern objects

Scope: High-level analyzer that orchestrates TypeScriptFunctionAnalyzer for function-level detection

Overview: Provides TypeScriptCQSAnalyzer class that coordinates CQS pattern detection in TypeScript
    code. Handles tree-sitter parsing with proper availability checking, returning empty results
    when tree-sitter is unavailable rather than raising exceptions. Delegates to
    TypeScriptFunctionAnalyzer to build CQSPattern objects for each function/method, which
    contain INPUT and OUTPUT operations along with function metadata (name, class context,
    async status).

Dependencies: TypeScriptBaseAnalyzer, TypeScriptFunctionAnalyzer, CQSConfig, CQSPattern

Exports: TypeScriptCQSAnalyzer

Interfaces: TypeScriptCQSAnalyzer.analyze(code, file_path, config) -> list[CQSPattern]

Implementation: Coordinates TypeScriptFunctionAnalyzer with tree-sitter availability checking
"""

from src.analyzers.typescript_base import TREE_SITTER_AVAILABLE, TypeScriptBaseAnalyzer

from .config import CQSConfig
from .types import CQSPattern
from .typescript_function_analyzer import TypeScriptFunctionAnalyzer


class TypeScriptCQSAnalyzer(TypeScriptBaseAnalyzer):
    """Analyzes TypeScript code for CQS patterns, returning per-function results."""

    def __init__(self) -> None:
        """Initialize analyzer with function analyzer."""
        super().__init__()
        self._function_analyzer = TypeScriptFunctionAnalyzer()

    def analyze(
        self,
        code: str,
        file_path: str,
        config: CQSConfig,
    ) -> list[CQSPattern]:
        """Analyze TypeScript code for CQS patterns in each function.

        Args:
            code: TypeScript source code to analyze
            file_path: Path to the source file (for error context)
            config: CQS configuration settings

        Returns:
            List of CQSPattern objects, one per function/method.
            Returns empty list if tree-sitter is unavailable or parsing fails.
        """
        if not TREE_SITTER_AVAILABLE:
            return []

        root_node = self.parse_typescript(code)
        if root_node is None:
            return []

        return self._function_analyzer.analyze(root_node, file_path, config)

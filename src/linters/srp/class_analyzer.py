"""
Purpose: Class analysis coordination for SRP linter

Scope: Coordinates Python and TypeScript class analysis

Overview: Provides unified class analysis interface for the SRP linter. Delegates to language-
    specific analyzers (PythonSRPAnalyzer, TypeScriptSRPAnalyzer) based on language type.
    Handles syntax error gracefully and extracts class metrics for SRP evaluation. Isolates
    language-specific analysis logic from rule checking and violation building.

Dependencies: ast, PythonSRPAnalyzer, TypeScriptSRPAnalyzer, BaseLintContext, SRPConfig

Exports: ClassAnalyzer

Interfaces: analyze_python(context, config) -> list[dict], analyze_typescript(context, config) -> list[dict]

Implementation: Delegates to language-specific analyzers, returns normalized metrics dicts
"""

import ast
from typing import Any

from src.core.base import BaseLintContext
from src.core.types import Severity, Violation

from .config import SRPConfig
from .python_analyzer import PythonSRPAnalyzer
from .typescript_analyzer import TypeScriptSRPAnalyzer


class ClassAnalyzer:
    """Coordinates class analysis for Python and TypeScript."""

    def __init__(self) -> None:
        """Initialize the class analyzer."""
        pass  # Coordinates analysis between language-specific analyzers

    def analyze_python(
        self, context: BaseLintContext, config: SRPConfig
    ) -> list[dict[str, Any]] | list[Violation]:
        """Analyze Python classes and return metrics or syntax errors.

        Args:
            context: Lint context with file information
            config: SRP configuration

        Returns:
            List of class metrics dicts, or list of syntax error violations
        """
        tree = self._parse_python_safely(context)
        if isinstance(tree, list):  # Syntax error violations
            return tree

        analyzer = PythonSRPAnalyzer()
        classes = analyzer.find_all_classes(tree)
        return [
            analyzer.analyze_class(class_node, context.file_content or "", config)
            for class_node in classes
        ]

    def analyze_typescript(
        self, context: BaseLintContext, config: SRPConfig
    ) -> list[dict[str, Any]]:
        """Analyze TypeScript classes and return metrics.

        Args:
            context: Lint context with file information
            config: SRP configuration

        Returns:
            List of class metrics dicts
        """
        analyzer = TypeScriptSRPAnalyzer()
        root_node = analyzer.parse_typescript(context.file_content or "")
        if not root_node:
            return []

        classes = analyzer.find_all_classes(root_node)
        return [
            analyzer.analyze_class(class_node, context.file_content or "", config)
            for class_node in classes
        ]

    def _parse_python_safely(self, context: BaseLintContext) -> ast.AST | list[Violation]:
        """Parse Python code and return AST or syntax error violations.

        Args:
            context: Lint context with file information

        Returns:
            AST if successful, list of syntax error violations otherwise
        """
        try:
            return ast.parse(context.file_content or "")
        except SyntaxError as exc:
            return [self._create_syntax_error_violation(exc, context)]

    def _create_syntax_error_violation(
        self, exc: SyntaxError, context: BaseLintContext
    ) -> Violation:
        """Create syntax error violation.

        Args:
            exc: SyntaxError exception
            context: Lint context

        Returns:
            Syntax error violation
        """
        return Violation(
            rule_id="srp.syntax-error",
            file_path=str(context.file_path or ""),
            line=exc.lineno or 1,
            column=exc.offset or 0,
            message=f"Syntax error: {exc.msg}",
            severity=Severity.ERROR,
        )

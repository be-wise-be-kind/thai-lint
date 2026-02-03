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
from .rust_analyzer import RustSRPAnalyzer
from .typescript_analyzer import TypeScriptSRPAnalyzer


class ClassAnalyzer:
    """Coordinates class analysis for Python and TypeScript."""

    def __init__(self) -> None:
        """Initialize the class analyzer with singleton analyzers."""
        # Singleton analyzers for performance (avoid recreating per-file)
        self._python_analyzer = PythonSRPAnalyzer()
        self._typescript_analyzer = TypeScriptSRPAnalyzer()
        self._rust_analyzer = RustSRPAnalyzer()

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

        classes = self._python_analyzer.find_all_classes(tree)
        return [
            self._python_analyzer.analyze_class(class_node, context.file_content or "", config)
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
        root_node = self._typescript_analyzer.parse_typescript(context.file_content or "")
        if not root_node:
            return []

        classes = self._typescript_analyzer.find_all_classes(root_node)
        return [
            self._typescript_analyzer.analyze_class(class_node, context.file_content or "", config)
            for class_node in classes
        ]

    def analyze_rust(self, context: BaseLintContext, config: SRPConfig) -> list[dict[str, Any]]:
        """Analyze Rust structs and return metrics.

        Finds all struct declarations and impl blocks, matches impl blocks to
        their target structs, and returns metrics for each struct.

        Args:
            context: Lint context with file information
            config: SRP configuration

        Returns:
            List of struct metrics dicts
        """
        root_node = self._rust_analyzer.parse_rust(context.file_content or "")
        if not root_node:
            return []

        structs = self._rust_analyzer.find_all_structs(root_node)
        impl_blocks = self._rust_analyzer.find_all_impl_blocks(root_node)
        impl_map = self._build_impl_map(impl_blocks)

        return [
            self._rust_analyzer.analyze_struct(
                struct_node,
                impl_map.get(self._rust_analyzer.get_impl_target_name(struct_node), []),
                context.file_content or "",
                config,
            )
            for struct_node in structs
        ]

    def _build_impl_map(self, impl_blocks: list) -> dict[str, list]:
        """Build mapping from struct name to its impl blocks.

        Args:
            impl_blocks: List of impl_item nodes

        Returns:
            Dictionary mapping struct names to lists of impl blocks
        """
        impl_map: dict[str, list] = {}
        for impl_node in impl_blocks:
            target_name = self._rust_analyzer.get_impl_target_name(impl_node)
            if target_name:
                impl_map.setdefault(target_name, []).append(impl_node)
        return impl_map

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

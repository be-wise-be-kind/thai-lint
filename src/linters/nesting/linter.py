"""
Purpose: Main nesting depth linter rule implementation

Scope: NestingDepthRule class implementing BaseLintRule interface

Overview: Implements nesting depth linter rule following BaseLintRule interface. Orchestrates
    configuration loading, Python/TypeScript analysis, and violation building through focused helper
    classes. Detects excessive nesting depth in functions using AST analysis. Supports configurable
    max_nesting_depth limit and ignore directives. Main rule class acts as coordinator for nesting
    depth checking workflow.

Dependencies: BaseLintRule, BaseLintContext, PythonNestingAnalyzer, TypeScriptNestingAnalyzer, NestingViolationBuilder

Exports: NestingDepthRule class

Interfaces: NestingDepthRule.check(context) -> list[Violation], properties for rule metadata

Implementation: Composition pattern with helper classes, AST-based analysis with configurable limits
"""

import ast
from typing import Any

from src.core.base import BaseLintContext, MultiLanguageLintRule
from src.core.linter_utils import load_linter_config
from src.core.types import Violation
from src.linter_config.ignore import IgnoreDirectiveParser

from .config import NestingConfig
from .python_analyzer import PythonNestingAnalyzer
from .typescript_analyzer import TypeScriptNestingAnalyzer
from .violation_builder import NestingViolationBuilder


class NestingDepthRule(MultiLanguageLintRule):
    """Detects excessive nesting depth in functions."""

    def __init__(self) -> None:
        """Initialize the nesting depth rule."""
        self._ignore_parser = IgnoreDirectiveParser()
        self._violation_builder = NestingViolationBuilder(self.rule_id)

    @property
    def rule_id(self) -> str:
        """Unique identifier for this rule."""
        return "nesting.excessive-depth"

    @property
    def rule_name(self) -> str:
        """Human-readable name for this rule."""
        return "Excessive Nesting Depth"

    @property
    def description(self) -> str:
        """Description of what this rule checks."""
        return "Functions should not have excessive nesting depth for better readability"

    def _load_config(self, context: BaseLintContext) -> NestingConfig:
        """Load configuration from context.

        Args:
            context: Lint context

        Returns:
            NestingConfig instance
        """
        return load_linter_config(context, "nesting", NestingConfig)

    def _process_python_functions(
        self, functions: list, analyzer: Any, config: NestingConfig, context: BaseLintContext
    ) -> list[Violation]:
        """Process Python functions and collect violations.

        Args:
            functions: List of function AST nodes
            analyzer: Python nesting analyzer
            config: Nesting configuration
            context: Lint context

        Returns:
            List of violations
        """
        violations = []
        for func in functions:
            max_depth, _line = analyzer.calculate_max_depth(func)
            if max_depth <= config.max_nesting_depth:
                continue

            violation = self._violation_builder.create_nesting_violation(
                func, max_depth, config, context
            )
            if not self._should_ignore(violation, context):
                violations.append(violation)
        return violations

    def _check_python(self, context: BaseLintContext, config: NestingConfig) -> list[Violation]:
        """Check Python code for nesting violations.

        Args:
            context: Lint context with Python file information
            config: Nesting configuration

        Returns:
            List of violations found in Python code
        """
        try:
            tree = ast.parse(context.file_content or "")
        except SyntaxError as e:
            return [self._violation_builder.create_syntax_error_violation(e, context)]

        analyzer = PythonNestingAnalyzer()
        functions = analyzer.find_all_functions(tree)
        return self._process_python_functions(functions, analyzer, config, context)

    def _process_typescript_functions(
        self, functions: list, analyzer: Any, config: NestingConfig, context: BaseLintContext
    ) -> list[Violation]:
        """Process TypeScript functions and collect violations.

        Args:
            functions: List of (function_node, function_name) tuples
            analyzer: TypeScript nesting analyzer
            config: Nesting configuration
            context: Lint context

        Returns:
            List of violations
        """
        violations = []
        for func_node, func_name in functions:
            max_depth, _line = analyzer.calculate_max_depth(func_node)
            if max_depth <= config.max_nesting_depth:
                continue

            violation = self._violation_builder.create_typescript_nesting_violation(
                (func_node, func_name), max_depth, config, context
            )
            if not self._should_ignore(violation, context):
                violations.append(violation)
        return violations

    def _check_typescript(self, context: BaseLintContext, config: NestingConfig) -> list[Violation]:
        """Check TypeScript code for nesting violations.

        Args:
            context: Lint context with TypeScript file information
            config: Nesting configuration

        Returns:
            List of violations found in TypeScript code
        """
        analyzer = TypeScriptNestingAnalyzer()
        root_node = analyzer.parse_typescript(context.file_content or "")
        if root_node is None:
            return []

        functions = analyzer.find_all_functions(root_node)
        return self._process_typescript_functions(functions, analyzer, config, context)

    def _should_ignore(self, violation: Violation, context: BaseLintContext) -> bool:
        """Check if violation should be ignored based on inline directives.

        Args:
            violation: Violation to check
            context: Lint context with file content

        Returns:
            True if violation should be ignored
        """
        return self._ignore_parser.should_ignore_violation(violation, context.file_content or "")

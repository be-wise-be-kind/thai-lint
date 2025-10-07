"""
Purpose: Main nesting depth linter rule implementation

Scope: NestingDepthRule class implementing BaseLintRule interface

Overview: Implements nesting depth linter rule following BaseLintRule interface. Detects excessive
    nesting depth in Python and TypeScript code using AST analysis. Supports configurable
    max_nesting_depth limit (default 4). Provides helpful violation messages with refactoring
    suggestions (early returns, guard clauses, extract method). Integrates with orchestrator for
    automatic rule discovery. Handles both Python (using ast) and TypeScript (using typescript-estree)
    code analysis. Gracefully handles syntax errors by reporting them as violations rather than
    crashing. Supports configuration loading from context metadata for per-file customization.

Dependencies: BaseLintRule, BaseLintContext, Violation, PythonNestingAnalyzer, TypeScriptNestingAnalyzer

Exports: NestingDepthRule class

Interfaces: NestingDepthRule.check(context) -> list[Violation], properties for rule metadata

Implementation: AST-based analysis with configurable limits and helpful error messages
"""

import ast
from typing import Any

from src.core.base import BaseLintContext, BaseLintRule
from src.core.types import Severity, Violation
from src.linter_config.ignore import IgnoreDirectiveParser

from .config import NestingConfig
from .python_analyzer import PythonNestingAnalyzer
from .typescript_analyzer import TypeScriptNestingAnalyzer


class NestingDepthRule(BaseLintRule):
    """Detects excessive nesting depth in functions."""

    def __init__(self) -> None:
        """Initialize the nesting depth rule."""
        self._ignore_parser = IgnoreDirectiveParser()

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

    def check(self, context: BaseLintContext) -> list[Violation]:
        """Check for excessive nesting depth violations.

        Args:
            context: Lint context with file information

        Returns:
            List of violations found
        """
        if context.file_content is None:
            return []

        # Load configuration
        config = self._load_config(context)
        if not config.enabled:
            return []

        # Analyze based on language
        if context.language == "python":
            return self._check_python(context, config)
        if context.language in ("typescript", "javascript"):
            return self._check_typescript(context, config)
        return []

    def _load_config(self, context: BaseLintContext) -> NestingConfig:
        """Load configuration from context metadata.

        Args:
            context: Lint context containing metadata

        Returns:
            NestingConfig instance with configuration values
        """
        metadata = getattr(context, "metadata", None)
        if metadata is None or not isinstance(metadata, dict):
            return NestingConfig()

        config_dict = metadata.get("nesting", {})
        if not isinstance(config_dict, dict):
            return NestingConfig()

        return NestingConfig.from_dict(config_dict)

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
            return [self._create_syntax_error_violation(e, context)]

        analyzer = PythonNestingAnalyzer()
        functions = analyzer.find_all_functions(tree)
        return self._check_functions(functions, config, context)

    def _check_functions(
        self,
        functions: list[ast.FunctionDef | ast.AsyncFunctionDef],
        config: NestingConfig,
        context: BaseLintContext,
    ) -> list[Violation]:
        """Check list of functions for nesting violations."""
        analyzer = PythonNestingAnalyzer()
        violations = []

        for func in functions:
            max_depth, _line = analyzer.calculate_max_depth(func)
            if max_depth > config.max_nesting_depth:
                violation = self._create_nesting_violation(func, max_depth, config, context)
                if not self._ignore_parser.should_ignore_violation(
                    violation, context.file_content or ""
                ):
                    violations.append(violation)

        return violations

    def _create_syntax_error_violation(
        self, error: SyntaxError, context: BaseLintContext
    ) -> Violation:
        """Create violation for syntax error."""
        return Violation(
            rule_id=self.rule_id,
            file_path=str(context.file_path or ""),
            line=error.lineno or 0,
            column=error.offset or 0,
            message=f"Syntax error: {error.msg}",
            severity=Severity.ERROR,
            suggestion="Fix syntax errors before checking nesting depth",
        )

    def _create_nesting_violation(
        self,
        func: ast.FunctionDef | ast.AsyncFunctionDef,
        max_depth: int,
        config: NestingConfig,
        context: BaseLintContext,
    ) -> Violation:
        """Create violation for excessive nesting."""
        return Violation(
            rule_id=self.rule_id,
            file_path=str(context.file_path or ""),
            line=func.lineno,
            column=func.col_offset,
            message=f"Function '{func.name}' has excessive nesting depth ({max_depth})",
            severity=Severity.ERROR,
            suggestion=(
                f"Maximum nesting depth of {max_depth} exceeds limit of {config.max_nesting_depth}. "
                "Consider extracting nested logic to separate functions, using early returns, "
                "or applying guard clauses to reduce nesting."
            ),
        )

    def _check_typescript(self, context: BaseLintContext, config: NestingConfig) -> list[Violation]:
        """Check TypeScript code for nesting violations."""
        analyzer = TypeScriptNestingAnalyzer()
        root_node = analyzer.parse_typescript(context.file_content or "")

        if root_node is None:
            return []

        functions = analyzer.find_all_functions(root_node)
        return self._check_typescript_functions(functions, config, context)

    def _check_typescript_functions(
        self, functions: list, config: NestingConfig, context: BaseLintContext
    ) -> list[Violation]:
        """Check TypeScript functions for nesting violations."""
        violations = []

        for func_node, func_name in functions:
            violation = self._check_single_typescript_function(
                func_node, func_name, config, context
            )
            if violation:
                violations.append(violation)

        return violations

    def _check_single_typescript_function(
        self, func_node: Any, func_name: str, config: NestingConfig, context: BaseLintContext
    ) -> Violation | None:
        """Check a single TypeScript function for nesting violations."""
        analyzer = TypeScriptNestingAnalyzer()
        max_depth, _line = analyzer.calculate_max_depth(func_node)

        if max_depth <= config.max_nesting_depth:
            return None

        violation = self._create_typescript_nesting_violation(
            func_node, func_name, max_depth, config, context
        )

        if self._ignore_parser.should_ignore_violation(violation, context.file_content or ""):
            return None

        return violation

    def _create_typescript_nesting_violation(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        func_node: Any,  # tree-sitter Node
        func_name: str,
        max_depth: int,
        config: NestingConfig,
        context: BaseLintContext,
    ) -> Violation:
        """Create violation for excessive nesting in TypeScript."""
        line = func_node.start_point[0] + 1  # Convert to 1-indexed
        column = func_node.start_point[1]

        return Violation(
            rule_id=self.rule_id,
            file_path=str(context.file_path or ""),
            line=line,
            column=column,
            message=f"Function '{func_name}' has excessive nesting depth ({max_depth})",
            severity=Severity.ERROR,
            suggestion=(
                f"Maximum nesting depth of {max_depth} exceeds limit of {config.max_nesting_depth}. "
                "Consider extracting nested logic to separate functions, using early returns, "
                "or applying guard clauses to reduce nesting."
            ),
        )

"""
Purpose: Main print statements linter rule implementation

Scope: Print and console statement detection for Python, TypeScript, and JavaScript files

Overview: Implements print statements linter rule following MultiLanguageLintRule interface. Orchestrates
    configuration loading, Python AST analysis for print() calls, TypeScript tree-sitter analysis
    for console.* calls, and violation building through focused helper classes. Detects print and
    console statements that should be replaced with proper logging. Supports configurable
    allow_in_scripts option to permit print() in __main__ blocks and configurable console_methods
    set for TypeScript/JavaScript. Handles ignore directives for suppressing specific violations
    through inline comments and configuration patterns.

Dependencies: BaseLintContext and MultiLanguageLintRule from core, ast module, pathlib,
    analyzer classes, config classes

Exports: PrintStatementRule class implementing MultiLanguageLintRule interface

Interfaces: check(context) -> list[Violation] for rule validation, standard rule properties
    (rule_id, rule_name, description)

Implementation: Composition pattern with helper classes (analyzers, violation builder),
    AST-based analysis for Python, tree-sitter for TypeScript/JavaScript
"""

import ast
from pathlib import Path

from src.core.base import BaseLintContext, MultiLanguageLintRule
from src.core.linter_utils import load_linter_config
from src.core.types import Violation
from src.linter_config.ignore import IgnoreDirectiveParser

from .config import PrintStatementConfig
from .python_analyzer import PythonPrintStatementAnalyzer
from .typescript_analyzer import TypeScriptPrintStatementAnalyzer
from .violation_builder import ViolationBuilder


class PrintStatementRule(MultiLanguageLintRule):  # thailint: ignore[srp]
    """Detects print/console statements that should be replaced with proper logging."""

    def __init__(self) -> None:
        """Initialize the print statements rule."""
        self._ignore_parser = IgnoreDirectiveParser()
        self._violation_builder = ViolationBuilder(self.rule_id)

    @property
    def rule_id(self) -> str:
        """Unique identifier for this rule."""
        return "print-statements.detected"

    @property
    def rule_name(self) -> str:
        """Human-readable name for this rule."""
        return "Print Statements"

    @property
    def description(self) -> str:
        """Description of what this rule checks."""
        return "Print/console statements should be replaced with proper logging"

    def _load_config(self, context: BaseLintContext) -> PrintStatementConfig:
        """Load configuration from context.

        Args:
            context: Lint context

        Returns:
            PrintStatementConfig instance
        """
        test_config = self._try_load_test_config(context)
        if test_config is not None:
            return test_config

        prod_config = self._try_load_production_config(context)
        if prod_config is not None:
            return prod_config

        return PrintStatementConfig()

    def _try_load_test_config(self, context: BaseLintContext) -> PrintStatementConfig | None:
        """Try to load test-style configuration."""
        if not hasattr(context, "config"):
            return None
        config_attr = context.config
        if config_attr is None or not isinstance(config_attr, dict):
            return None
        return PrintStatementConfig.from_dict(config_attr, context.language)

    def _try_load_production_config(self, context: BaseLintContext) -> PrintStatementConfig | None:
        """Try to load production configuration."""
        if not hasattr(context, "metadata") or not isinstance(context.metadata, dict):
            return None

        metadata = context.metadata

        if "print_statements" in metadata:
            return load_linter_config(context, "print_statements", PrintStatementConfig)

        if "print-statements" in metadata:
            return load_linter_config(context, "print-statements", PrintStatementConfig)

        return None

    def _is_file_ignored(self, context: BaseLintContext, config: PrintStatementConfig) -> bool:
        """Check if file matches ignore patterns.

        Args:
            context: Lint context
            config: Print statements configuration

        Returns:
            True if file should be ignored
        """
        if not config.ignore:
            return False

        if not context.file_path:
            return False

        file_path = Path(context.file_path)
        for pattern in config.ignore:
            if self._matches_pattern(file_path, pattern):
                return True
        return False

    def _matches_pattern(self, file_path: Path, pattern: str) -> bool:
        """Check if file path matches a glob pattern.

        Args:
            file_path: Path to check
            pattern: Glob pattern

        Returns:
            True if path matches pattern
        """
        if file_path.match(pattern):
            return True
        if pattern in str(file_path):
            return True
        return False

    def _check_python(
        self, context: BaseLintContext, config: PrintStatementConfig
    ) -> list[Violation]:
        """Check Python code for print() violations.

        Args:
            context: Lint context with Python file information
            config: Print statements configuration

        Returns:
            List of violations found in Python code
        """
        if self._is_file_ignored(context, config):
            return []

        tree = self._parse_python_code(context.file_content)
        if tree is None:
            return []

        analyzer = PythonPrintStatementAnalyzer()
        print_calls = analyzer.find_print_calls(tree)
        return self._collect_python_violations(print_calls, context, config, analyzer)

    def _parse_python_code(self, code: str | None) -> ast.AST | None:
        """Parse Python code into AST."""
        try:
            return ast.parse(code or "")
        except SyntaxError:
            return None

    def _collect_python_violations(
        self,
        print_calls: list,
        context: BaseLintContext,
        config: PrintStatementConfig,
        analyzer: PythonPrintStatementAnalyzer,
    ) -> list[Violation]:
        """Collect violations from Python print() calls.

        Args:
            print_calls: List of (node, parent, line_number) tuples
            context: Lint context
            config: Configuration
            analyzer: Python analyzer instance

        Returns:
            List of violations
        """
        violations = []
        for node, _parent, line_number in print_calls:
            violation = self._try_create_python_violation(
                node, line_number, context, config, analyzer
            )
            if violation is not None:
                violations.append(violation)
        return violations

    def _try_create_python_violation(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        node: ast.Call,
        line_number: int,
        context: BaseLintContext,
        config: PrintStatementConfig,
        analyzer: PythonPrintStatementAnalyzer,
    ) -> Violation | None:
        """Try to create a violation for a Python print() call.

        Args:
            node: AST Call node
            line_number: Line number
            context: Lint context
            config: Configuration
            analyzer: Python analyzer

        Returns:
            Violation or None if should not flag
        """
        # Check if in __main__ block and allow_in_scripts is enabled
        if config.allow_in_scripts and analyzer.is_in_main_block(node):
            return None

        violation = self._violation_builder.create_python_violation(
            node, line_number, context.file_path
        )

        if self._should_ignore(violation, context):
            return None

        return violation

    def _should_ignore(self, violation: Violation, context: BaseLintContext) -> bool:
        """Check if violation should be ignored based on inline directives.

        Args:
            violation: Violation to check
            context: Lint context with file content

        Returns:
            True if violation should be ignored
        """
        if self._ignore_parser.should_ignore_violation(violation, context.file_content or ""):
            return True
        return self._check_generic_ignore(violation, context)

    def _check_generic_ignore(self, violation: Violation, context: BaseLintContext) -> bool:
        """Check for generic ignore directives.

        Args:
            violation: Violation to check
            context: Lint context

        Returns:
            True if line has generic ignore directive
        """
        line_text = self._get_violation_line(violation, context)
        if line_text is None:
            return False
        return self._has_generic_ignore_directive(line_text)

    def _get_violation_line(self, violation: Violation, context: BaseLintContext) -> str | None:
        """Get the line text for a violation."""
        if not context.file_content:
            return None

        lines = context.file_content.splitlines()
        if violation.line <= 0 or violation.line > len(lines):
            return None

        return lines[violation.line - 1].lower()

    def _has_generic_ignore_directive(self, line_text: str) -> bool:
        """Check if line has generic ignore directive."""
        if self._has_generic_thailint_ignore(line_text):
            return True
        return self._has_noqa_directive(line_text)

    def _has_generic_thailint_ignore(self, line_text: str) -> bool:
        """Check for generic thailint: ignore (no brackets)."""
        if "# thailint: ignore" not in line_text:
            return False
        after_ignore = line_text.split("# thailint: ignore")[1].split("#")[0]
        return "[" not in after_ignore

    def _has_noqa_directive(self, line_text: str) -> bool:
        """Check for noqa-style comments."""
        return "# noqa" in line_text

    def _check_typescript(
        self, context: BaseLintContext, config: PrintStatementConfig
    ) -> list[Violation]:
        """Check TypeScript/JavaScript code for console.* violations.

        Args:
            context: Lint context with TypeScript/JavaScript file information
            config: Print statements configuration

        Returns:
            List of violations found in TypeScript/JavaScript code
        """
        if self._is_file_ignored(context, config):
            return []

        analyzer = TypeScriptPrintStatementAnalyzer()
        root_node = analyzer.parse_typescript(context.file_content or "")
        if root_node is None:
            return []

        console_calls = analyzer.find_console_calls(root_node, config.console_methods)
        return self._collect_typescript_violations(console_calls, context)

    def _collect_typescript_violations(
        self,
        console_calls: list,
        context: BaseLintContext,
    ) -> list[Violation]:
        """Collect violations from TypeScript console.* calls.

        Args:
            console_calls: List of (node, method_name, line_number) tuples
            context: Lint context

        Returns:
            List of violations
        """
        violations = []
        for _node, method_name, line_number in console_calls:
            violation = self._try_create_typescript_violation(method_name, line_number, context)
            if violation is not None:
                violations.append(violation)
        return violations

    def _try_create_typescript_violation(
        self,
        method_name: str,
        line_number: int,
        context: BaseLintContext,
    ) -> Violation | None:
        """Try to create a violation for a TypeScript console.* call.

        Args:
            method_name: Console method name (log, warn, etc.)
            line_number: Line number
            context: Lint context

        Returns:
            Violation or None if should not flag
        """
        # Check if test file (skip test files)
        if self._is_test_file(context.file_path):
            return None

        violation = self._violation_builder.create_typescript_violation(
            method_name, line_number, context.file_path
        )

        if self._should_ignore_typescript(violation, context):
            return None

        return violation

    def _is_test_file(self, file_path: object) -> bool:
        """Check if file is a test file.

        Args:
            file_path: Path to check

        Returns:
            True if test file
        """
        path_str = str(file_path)
        return any(
            pattern in path_str
            for pattern in [".test.", ".spec.", "test_", "_test.", "/tests/", "/test/"]
        )

    def _should_ignore_typescript(self, violation: Violation, context: BaseLintContext) -> bool:
        """Check if TypeScript violation should be ignored.

        Args:
            violation: Violation to check
            context: Lint context

        Returns:
            True if should ignore
        """
        if self._ignore_parser.should_ignore_violation(violation, context.file_content or ""):
            return True
        return self._check_typescript_ignore(violation, context)

    def _check_typescript_ignore(self, violation: Violation, context: BaseLintContext) -> bool:
        """Check for TypeScript-style ignore directives.

        Args:
            violation: Violation to check
            context: Lint context

        Returns:
            True if line has ignore directive
        """
        line_text = self._get_violation_line(violation, context)
        if line_text is None:
            return False
        return self._has_typescript_ignore_directive(line_text)

    def _has_typescript_ignore_directive(self, line_text: str) -> bool:
        """Check if line has TypeScript-style ignore directive.

        Args:
            line_text: Line text to check

        Returns:
            True if has ignore directive
        """
        if "// thailint: ignore[print-statements]" in line_text:
            return True

        if "// thailint: ignore" in line_text:
            after_ignore = line_text.split("// thailint: ignore")[1].split("//")[0]
            if "[" not in after_ignore:
                return True

        if "// noqa" in line_text:
            return True

        return False

"""
Purpose: Lint rule for detecting conditional verbose logging anti-patterns

Scope: Detection of if verbose: logger.*() patterns in Python code

Overview: Implements the ConditionalVerboseRule that detects logging calls conditionally guarded
    by verbose flags. This is an anti-pattern because logging levels should be configured through
    the logging framework (e.g., logger.setLevel(logging.DEBUG)) rather than through code
    conditionals. The rule reports violations with suggestions to remove the conditional and
    configure logging levels properly. Only applies to Python files as this pattern is specific
    to Python logging practices.

Dependencies: BaseLintContext and BaseLintRule from core, ast module, conditional_verbose_analyzer

Exports: ConditionalVerboseRule class implementing BaseLintRule interface

Interfaces: check(context) -> list[Violation] for rule validation, standard rule properties
    (rule_id, rule_name, description)

Implementation: AST-based analysis using ConditionalVerboseAnalyzer for pattern detection
"""

import ast
from pathlib import Path

from src.core.base import BaseLintContext, BaseLintRule
from src.core.constants import Language
from src.core.linter_utils import has_file_content, load_linter_config
from src.core.types import Violation
from src.core.violation_utils import get_violation_line, has_python_noqa
from src.linter_config.ignore import get_ignore_parser

from .conditional_verbose_analyzer import ConditionalVerboseAnalyzer
from .config import PrintStatementConfig


class ConditionalVerboseRule(BaseLintRule):
    """Detects conditional verbose logging patterns that should use log level configuration."""

    def __init__(self) -> None:
        """Initialize the conditional verbose rule."""
        self._ignore_parser = get_ignore_parser()

    @property
    def rule_id(self) -> str:
        """Unique identifier for this rule."""
        return "improper-logging.conditional-verbose"

    @property
    def rule_name(self) -> str:
        """Human-readable name for this rule."""
        return "Improper Logging - Conditional Verbose"

    @property
    def description(self) -> str:
        """Description of what this rule checks."""
        return "Conditional verbose logging should use log level configuration instead"

    def check(self, context: BaseLintContext) -> list[Violation]:
        """Check for conditional verbose logging violations.

        Only applies to Python files, as this pattern is Python-specific.

        Args:
            context: Lint context with file information

        Returns:
            List of violations found
        """
        if not self._should_analyze(context):
            return []

        tree = self._parse_python_code(context.file_content)
        if tree is None:
            return []

        analyzer = ConditionalVerboseAnalyzer()
        conditional_calls = analyzer.find_conditional_verbose_calls(tree)

        return self._collect_violations(conditional_calls, context)

    def _should_analyze(self, context: BaseLintContext) -> bool:
        """Check if this file should be analyzed."""
        if not has_file_content(context):
            return False
        if context.language != Language.PYTHON:
            return False
        config = self._load_config(context)
        if not config.enabled:
            return False
        return not self._is_file_ignored(context, config)

    def _load_config(self, context: BaseLintContext) -> PrintStatementConfig:
        """Load configuration from context.

        Uses the same config as print-statements linter for consistency.

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
        config_keys = ("print_statements", "print-statements", "improper-logging")

        for key in config_keys:
            if key in metadata:
                return load_linter_config(context, key, PrintStatementConfig)

        return None

    def _is_file_ignored(self, context: BaseLintContext, config: PrintStatementConfig) -> bool:
        """Check if file matches ignore patterns."""
        if not config.ignore:
            return False
        if not context.file_path:
            return False

        file_path = Path(context.file_path)
        return any(self._matches_pattern(file_path, pattern) for pattern in config.ignore)

    def _matches_pattern(self, file_path: Path, pattern: str) -> bool:
        """Check if file path matches a glob pattern."""
        if file_path.match(pattern):
            return True
        if pattern in str(file_path):
            return True
        return False

    def _parse_python_code(self, code: str | None) -> ast.AST | None:
        """Parse Python code into AST."""
        try:
            return ast.parse(code or "")
        except SyntaxError:
            return None

    def _collect_violations(
        self,
        conditional_calls: list[tuple[ast.If, ast.Call, str, int]],
        context: BaseLintContext,
    ) -> list[Violation]:
        """Collect violations from conditional verbose logging patterns.

        Args:
            conditional_calls: List of (if_node, call_node, method_name, line_number) tuples
            context: Lint context

        Returns:
            List of violations
        """
        violations = []
        for _if_node, _call_node, method_name, line_number in conditional_calls:
            violation = self._create_violation(method_name, line_number, context)
            if not self._should_ignore(violation, context):
                violations.append(violation)
        return violations

    def _create_violation(
        self,
        method_name: str,
        line: int,
        context: BaseLintContext,
    ) -> Violation:
        """Create a violation for a conditional verbose logging pattern.

        Args:
            method_name: The logger method name (debug, info, etc.)
            line: Line number where the violation occurs
            context: Lint context

        Returns:
            Violation object with details about the pattern
        """
        message = f"Conditional verbose check around logger.{method_name}() should be removed"
        suggestion = (
            "Remove the 'if verbose:' condition and configure logging level instead. "
            "Use logger.setLevel(logging.DEBUG) to control verbosity."
        )

        return Violation(
            rule_id=self.rule_id,
            file_path=str(context.file_path) if context.file_path else "",
            line=line,
            column=0,
            message=message,
            suggestion=suggestion,
        )

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
        line_text = get_violation_line(violation, context)
        if line_text is None:
            return False
        return self._has_generic_ignore_directive(line_text)

    def _has_generic_ignore_directive(self, line_text: str) -> bool:
        """Check if line has generic ignore directive."""
        if self._has_generic_thailint_ignore(line_text):
            return True
        return has_python_noqa(line_text)

    def _has_generic_thailint_ignore(self, line_text: str) -> bool:
        """Check for generic thailint: ignore (no brackets)."""
        if "# thailint: ignore" not in line_text:
            return False
        after_ignore = line_text.split("# thailint: ignore")[1].split("#")[0]
        return "[" not in after_ignore

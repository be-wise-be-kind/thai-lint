"""
Purpose: Regex compilation in loop linter rule implementation

Scope: RegexInLoopRule class implementing MultiLanguageLintRule interface

Overview: Implements regex-in-loop linter rule following MultiLanguageLintRule interface.
    Orchestrates configuration loading, Python analysis, and violation building through
    focused helper classes. Detects repeated regex compilation patterns using re.method()
    calls in loops instead of pre-compiled patterns. Supports configurable enabled flag
    and ignore directives. Main rule class acts as coordinator for regex detection workflow.

Dependencies: MultiLanguageLintRule, BaseLintContext, PythonRegexInLoopAnalyzer,
    PerformanceViolationBuilder

Exports: RegexInLoopRule class

Interfaces: RegexInLoopRule.check(context) -> list[Violation], properties for rule metadata

Implementation: Composition pattern with analyzer classes, AST-based analysis

"""

from typing import Any

from src.core.base import BaseLintContext, MultiLanguageLintRule
from src.core.linter_utils import load_linter_config, with_parsed_python
from src.core.types import Violation
from src.linter_config.ignore import get_ignore_parser

from .config import PerformanceConfig
from .regex_analyzer import PythonRegexInLoopAnalyzer
from .violation_builder import PerformanceViolationBuilder


class RegexInLoopRule(MultiLanguageLintRule):
    """Detects regex compilation in loops."""

    def __init__(self) -> None:
        """Initialize the regex in loop rule."""
        self._ignore_parser = get_ignore_parser()
        self._violation_builder = PerformanceViolationBuilder(self.rule_id)
        self._python_analyzer = PythonRegexInLoopAnalyzer()

    @property
    def rule_id(self) -> str:
        """Unique identifier for this rule."""
        return "performance.regex-in-loop"

    @property
    def rule_name(self) -> str:
        """Human-readable name for this rule."""
        return "Regex Compilation in Loop"

    @property
    def description(self) -> str:
        """Description of what this rule checks."""
        return "re.method() in loops recompiles pattern each iteration; use re.compile() instead"

    def _load_config(self, context: BaseLintContext) -> PerformanceConfig:
        """Load configuration from context.

        Args:
            context: Lint context

        Returns:
            PerformanceConfig instance
        """
        return load_linter_config(context, "performance", PerformanceConfig)

    def _check_python(self, context: BaseLintContext, config: PerformanceConfig) -> list[Violation]:
        """Check Python code for regex compilation in loops.

        Args:
            context: Lint context with Python file information
            config: Performance configuration

        Returns:
            List of violations found in Python code
        """
        return with_parsed_python(
            context,
            self._violation_builder,
            lambda tree: self._analyze_python_regex(tree, context),
        )

    def _analyze_python_regex(self, tree: Any, context: BaseLintContext) -> list[Violation]:
        """Analyze parsed Python AST for regex in loops."""
        violations_raw = self._python_analyzer.find_violations(tree)
        return self._build_violations(violations_raw, context)

    def _check_typescript(
        self, context: BaseLintContext, config: PerformanceConfig
    ) -> list[Violation]:
        """Check TypeScript code for regex compilation in loops.

        Args:
            context: Lint context with TypeScript file information
            config: Performance configuration

        Returns:
            Empty list - TypeScript regex handling is different from Python
        """
        # TypeScript uses RegExp objects differently, not implemented
        return []

    def _build_violations(self, raw_violations: list, context: BaseLintContext) -> list[Violation]:
        """Build Violation objects from analyzer results.

        Args:
            raw_violations: List of RegexInLoopViolation dataclass instances
            context: Lint context

        Returns:
            List of Violation objects
        """
        violations = []
        for v in raw_violations:
            violation = self._violation_builder.create_regex_in_loop_violation(
                method_name=v.method_name,
                line_number=v.line_number,
                column=v.column,
                loop_type=v.loop_type,
                context=context,
            )
            if not self._should_ignore(violation, context):
                violations.append(violation)
        return violations

    def _should_ignore(self, violation: Violation, context: BaseLintContext) -> bool:
        """Check if violation should be ignored based on inline directives.

        Args:
            violation: Violation to check
            context: Lint context with file content

        Returns:
            True if violation should be ignored
        """
        return self._ignore_parser.should_ignore_violation(violation, context.file_content or "")

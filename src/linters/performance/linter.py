"""
Purpose: Main string concatenation in loop linter rule implementation

Scope: StringConcatLoopRule class implementing MultiLanguageLintRule interface

Overview: Implements string-concat-loop linter rule following MultiLanguageLintRule interface.
    Orchestrates configuration loading, Python/TypeScript analysis, and violation building
    through focused helper classes. Detects O(n²) string building patterns using += in loops.
    Supports configurable enabled flag and ignore directives. Main rule class acts as
    coordinator for string concatenation detection workflow.

Dependencies: MultiLanguageLintRule, BaseLintContext, PythonStringConcatAnalyzer,
    TypeScriptStringConcatAnalyzer, PerformanceViolationBuilder

Exports: StringConcatLoopRule class

Interfaces: StringConcatLoopRule.check(context) -> list[Violation], properties for rule metadata

Implementation: Composition pattern with analyzer classes, AST-based analysis

"""

from typing import Any

from src.core.base import BaseLintContext, MultiLanguageLintRule
from src.core.linter_utils import load_linter_config, with_parsed_python
from src.core.types import Violation
from src.linter_config.ignore import get_ignore_parser

from .config import PerformanceConfig
from .python_analyzer import PythonStringConcatAnalyzer
from .typescript_analyzer import TypeScriptStringConcatAnalyzer
from .violation_builder import PerformanceViolationBuilder


class StringConcatLoopRule(MultiLanguageLintRule):
    """Detects O(n²) string concatenation in loops."""

    def __init__(self) -> None:
        """Initialize the string concat loop rule."""
        self._ignore_parser = get_ignore_parser()
        self._violation_builder = PerformanceViolationBuilder(self.rule_id)
        # Singleton analyzers for performance
        self._python_analyzer = PythonStringConcatAnalyzer()
        self._typescript_analyzer = TypeScriptStringConcatAnalyzer()

    @property
    def rule_id(self) -> str:
        """Unique identifier for this rule."""
        return "performance.string-concat-loop"

    @property
    def rule_name(self) -> str:
        """Human-readable name for this rule."""
        return "String Concatenation in Loop"

    @property
    def description(self) -> str:
        """Description of what this rule checks."""
        return "String += in loops creates O(n²) complexity; use join() instead"

    def _load_config(self, context: BaseLintContext) -> PerformanceConfig:
        """Load configuration from context.

        Args:
            context: Lint context

        Returns:
            PerformanceConfig instance
        """
        return load_linter_config(context, "performance", PerformanceConfig)

    def _check_python(self, context: BaseLintContext, config: PerformanceConfig) -> list[Violation]:
        """Check Python code for string concatenation in loops.

        Args:
            context: Lint context with Python file information
            config: Performance configuration

        Returns:
            List of violations found in Python code
        """
        return with_parsed_python(
            context,
            self._violation_builder,
            lambda tree: self._analyze_python_string_concat(tree, context),
        )

    def _analyze_python_string_concat(self, tree: Any, context: BaseLintContext) -> list[Violation]:
        """Analyze parsed Python AST for string concatenation in loops."""
        violations_raw = self._python_analyzer.find_violations(tree)
        violations_deduped = self._python_analyzer.deduplicate_violations(violations_raw)
        return self._build_violations(violations_deduped, context)

    def _check_typescript(
        self, context: BaseLintContext, config: PerformanceConfig
    ) -> list[Violation]:
        """Check TypeScript code for string concatenation in loops.

        Args:
            context: Lint context with TypeScript file information
            config: Performance configuration

        Returns:
            List of violations found in TypeScript code
        """
        root_node = self._typescript_analyzer.parse_typescript(context.file_content or "")
        if root_node is None:
            return []

        violations_raw = self._typescript_analyzer.find_violations(root_node)
        violations_deduped = self._typescript_analyzer.deduplicate_violations(violations_raw)

        return self._build_violations(violations_deduped, context)

    def _build_violations(self, raw_violations: list, context: BaseLintContext) -> list[Violation]:
        """Build Violation objects from analyzer results.

        Args:
            raw_violations: List of StringConcatViolation dataclass instances
            context: Lint context

        Returns:
            List of Violation objects
        """
        violations = []
        for v in raw_violations:
            violation = self._violation_builder.create_string_concat_violation(
                variable_name=v.variable_name,
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

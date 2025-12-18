"""
Purpose: Main SRP linter rule implementation

Scope: SRPRule class implementing BaseLintRule interface

Overview: Implements Single Responsibility Principle linter rule following BaseLintRule interface.
    Orchestrates configuration loading, class analysis, metrics evaluation, and violation building
    through focused helper classes. Detects classes with too many methods, excessive lines of code,
    or generic naming patterns. Supports configurable thresholds and ignore directives. Handles both
    Python and TypeScript code analysis. Main rule class acts as coordinator for SRP checking workflow.

Dependencies: BaseLintRule, BaseLintContext, Violation, ClassAnalyzer, MetricsEvaluator, ViolationBuilder

Exports: SRPRule class

Interfaces: SRPRule.check(context) -> list[Violation], properties for rule metadata

Implementation: Composition pattern with helper classes, heuristic-based SRP analysis
"""

from src.core.base import BaseLintContext, MultiLanguageLintRule
from src.core.linter_utils import load_linter_config
from src.core.types import Violation
from src.linter_config.ignore import IgnoreDirectiveParser

from .class_analyzer import ClassAnalyzer
from .config import SRPConfig
from .metrics_evaluator import evaluate_metrics
from .violation_builder import ViolationBuilder


class SRPRule(MultiLanguageLintRule):
    """Detects Single Responsibility Principle violations in classes."""

    def __init__(self) -> None:
        """Initialize the SRP rule."""
        self._ignore_parser = IgnoreDirectiveParser()
        self._class_analyzer = ClassAnalyzer()
        self._violation_builder = ViolationBuilder()

    @property
    def rule_id(self) -> str:
        """Unique identifier for this rule."""
        return "srp.violation"

    @property
    def rule_name(self) -> str:
        """Human-readable name for this rule."""
        return "Single Responsibility Principle"

    @property
    def description(self) -> str:
        """Description of what this rule checks."""
        return "Classes should have a single, well-defined responsibility"

    def check(self, context: BaseLintContext) -> list[Violation]:
        """Check for SRP violations with custom ignore pattern handling.

        Overrides parent to add file-level ignore pattern checking before dispatch.

        Args:
            context: Lint context with file information

        Returns:
            List of violations found
        """
        from src.core.linter_utils import has_file_content

        if not has_file_content(context):
            return []

        config = self._load_config(context)
        if not self._should_process_file(context, config):
            return []

        # Standard language dispatch
        return self._dispatch_by_language(context, config)

    def _should_process_file(self, context: BaseLintContext, config: SRPConfig) -> bool:
        """Check if file should be processed.

        Args:
            context: Lint context
            config: SRP configuration

        Returns:
            True if file should be processed
        """
        if not config.enabled:
            return False
        return not self._is_file_ignored(context, config)

    def _dispatch_by_language(self, context: BaseLintContext, config: SRPConfig) -> list[Violation]:
        """Dispatch to language-specific checker.

        Args:
            context: Lint context
            config: SRP configuration

        Returns:
            List of violations found
        """
        if context.language == "python":
            return self._check_python(context, config)

        if context.language in ("typescript", "javascript"):
            return self._check_typescript(context, config)

        return []

    def _load_config(self, context: BaseLintContext) -> SRPConfig:
        """Load configuration from context.

        Args:
            context: Lint context

        Returns:
            SRPConfig instance
        """
        return load_linter_config(context, "srp", SRPConfig)

    def _is_file_ignored(self, context: BaseLintContext, config: SRPConfig) -> bool:
        """Check if file matches ignore patterns.

        Args:
            context: Lint context
            config: SRP configuration

        Returns:
            True if file should be ignored
        """
        if not config.ignore:
            return False

        file_path = str(context.file_path)
        for pattern in config.ignore:
            if pattern in file_path:
                return True
        return False

    def _check_python(self, context: BaseLintContext, config: SRPConfig) -> list[Violation]:
        """Check Python code for SRP violations.

        Args:
            context: Lint context with file information
            config: SRP configuration

        Returns:
            List of violations found
        """
        results = self._class_analyzer.analyze_python(context, config)
        if results and isinstance(results[0], Violation):  # Syntax errors
            return results  # type: ignore[return-value]

        return self._build_violations_from_metrics(results, config, context)

    def _build_violations_from_metrics(
        self,
        metrics_list: list,
        config: SRPConfig,
        context: BaseLintContext,
    ) -> list[Violation]:
        """Build violations from class metrics.

        Args:
            metrics_list: List of class metrics
            config: SRP configuration
            context: Lint context

        Returns:
            List of violations
        """
        violations = []
        valid_metrics = (m for m in metrics_list if isinstance(m, dict))
        for metrics in valid_metrics:
            violation = self._create_violation_if_needed(metrics, config, context)
            if violation:
                violations.append(violation)
        return violations

    def _create_violation_if_needed(
        self,
        metrics: dict,
        config: SRPConfig,
        context: BaseLintContext,
    ) -> Violation | None:
        """Create violation if metrics exceed thresholds.

        Args:
            metrics: Class metrics dictionary
            config: SRP configuration
            context: Lint context

        Returns:
            Violation or None if no issues or should be ignored
        """
        issues = evaluate_metrics(metrics, config)
        if not issues:
            return None

        violation = self._violation_builder.build_violation(metrics, issues, self.rule_id, context)
        if self._should_ignore(violation, context):
            return None

        return violation

    def _check_typescript(self, context: BaseLintContext, config: SRPConfig) -> list[Violation]:
        """Check TypeScript code for SRP violations.

        Args:
            context: Lint context with file information
            config: SRP configuration

        Returns:
            List of violations found
        """
        metrics_list = self._class_analyzer.analyze_typescript(context, config)
        return self._build_violations_from_metrics(metrics_list, config, context)

    def _should_ignore(self, violation: Violation, context: BaseLintContext) -> bool:
        """Check if violation should be ignored based on inline directives.

        Args:
            violation: Violation to check
            context: Lint context with file content

        Returns:
            True if violation should be ignored
        """
        if context.file_content is None:
            return False

        return self._ignore_parser.should_ignore_violation(violation, context.file_content)

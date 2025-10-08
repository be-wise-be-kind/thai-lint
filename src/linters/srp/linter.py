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

from src.core.base import BaseLintContext, BaseLintRule
from src.core.types import Violation
from src.linter_config.ignore import IgnoreDirectiveParser

from .class_analyzer import ClassAnalyzer
from .config import SRPConfig
from .metrics_evaluator import evaluate_metrics
from .violation_builder import ViolationBuilder


class SRPRule(BaseLintRule):
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
        """Check for SRP violations.

        Args:
            context: Lint context with file information

        Returns:
            List of violations found
        """
        if not context.file_content:
            return []

        config = self._load_config(context)
        if not config.enabled:
            return []
        if self._is_file_ignored(context, config):
            return []

        return self._analyze_by_language(context, config)

    def _analyze_by_language(self, context: BaseLintContext, config: SRPConfig) -> list[Violation]:
        """Analyze based on language type."""
        if context.language == "python":
            return self._check_python(context, config)
        if context.language in ("typescript", "javascript"):
            return self._check_typescript(context, config)
        return []

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

    def _load_config(self, context: BaseLintContext) -> SRPConfig:
        """Load configuration from context metadata with language-specific overrides.

        Args:
            context: Lint context containing metadata

        Returns:
            SRPConfig instance with configuration values for the specific language
        """
        metadata = getattr(context, "metadata", None)
        if metadata is None or not isinstance(metadata, dict):
            return SRPConfig()

        config_dict = metadata.get("srp", {})
        if not isinstance(config_dict, dict):
            return SRPConfig()

        # Pass language to get language-specific thresholds
        language = getattr(context, "language", None)
        return SRPConfig.from_dict(config_dict, language=language)

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
            return results  # type: ignore

        return self._build_violations_from_metrics(results, context, config)  # type: ignore

    def _check_typescript(self, context: BaseLintContext, config: SRPConfig) -> list[Violation]:
        """Check TypeScript code for SRP violations.

        Args:
            context: Lint context with file information
            config: SRP configuration

        Returns:
            List of violations found
        """
        metrics_list = self._class_analyzer.analyze_typescript(context, config)
        return self._build_violations_from_metrics(metrics_list, context, config)

    def _build_violations_from_metrics(
        self, metrics_list: list, context: BaseLintContext, config: SRPConfig
    ) -> list[Violation]:
        """Build violations from class metrics.

        Args:
            metrics_list: List of class metrics dicts
            context: Lint context
            config: SRP configuration

        Returns:
            List of violations (filtered by ignore directives)
        """
        violations = []
        for metrics in metrics_list:
            issues = evaluate_metrics(metrics, config)
            if not issues:
                continue

            violation = self._violation_builder.build_violation(
                metrics, issues, self.rule_id, context
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
        if context.file_content is None:
            return False

        return self._ignore_parser.should_ignore_violation(violation, context.file_content)

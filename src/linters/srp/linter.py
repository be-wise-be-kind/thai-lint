"""
Purpose: Main SRP linter rule implementation

Scope: SRPRule class implementing BaseLintRule interface

Overview: Implements Single Responsibility Principle linter rule following BaseLintRule interface.
    Detects classes with too many methods, excessive lines of code, or generic naming patterns
    that indicate SRP violations. Supports configurable thresholds (max_methods, max_loc) and
    keyword detection. Provides helpful violation messages with refactoring suggestions (extract
    class, split responsibilities). Integrates with orchestrator for automatic rule discovery.
    Handles both Python (using ast) and TypeScript (using tree-sitter) code analysis. Supports
    ignore directives for suppressing specific violations. Returns violations with severity,
    location, and actionable suggestions.

Dependencies: BaseLintRule, BaseLintContext, Violation, PythonSRPAnalyzer, TypeScriptSRPAnalyzer

Exports: SRPRule class

Interfaces: SRPRule.check(context) -> list[Violation], properties for rule metadata

Implementation: Heuristic-based SRP analysis with configurable thresholds and helpful suggestions
"""

import ast
from typing import Any

from src.core.base import BaseLintContext, BaseLintRule
from src.core.types import Severity, Violation
from src.linter_config.ignore import IgnoreDirectiveParser

from .config import SRPConfig
from .python_analyzer import PythonSRPAnalyzer
from .typescript_analyzer import TypeScriptSRPAnalyzer


class SRPRule(BaseLintRule):
    """Detects Single Responsibility Principle violations in classes."""

    def __init__(self) -> None:
        """Initialize the SRP rule."""
        self._ignore_parser = IgnoreDirectiveParser()

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

    def _load_config(self, context: BaseLintContext) -> SRPConfig:
        """Load configuration from context metadata.

        Args:
            context: Lint context containing metadata

        Returns:
            SRPConfig instance with configuration values
        """
        metadata = getattr(context, "metadata", None)
        if metadata is None or not isinstance(metadata, dict):
            return SRPConfig()

        config_dict = metadata.get("srp", {})
        if not isinstance(config_dict, dict):
            return SRPConfig()

        return SRPConfig.from_dict(config_dict)

    def _check_python(self, context: BaseLintContext, config: SRPConfig) -> list[Violation]:
        """Check Python code for SRP violations.

        Args:
            context: Lint context with file information
            config: SRP configuration

        Returns:
            List of violations found
        """
        tree = self._parse_python_safely(context)
        if isinstance(tree, list):  # Syntax error violations
            return tree

        analyzer = PythonSRPAnalyzer()
        classes = analyzer.find_all_classes(tree)
        return self._analyze_classes(classes, analyzer, context, config)

    def _parse_python_safely(self, context: BaseLintContext) -> ast.AST | list[Violation]:
        """Parse Python code and return AST or syntax error violations."""
        try:
            return ast.parse(context.file_content or "")
        except SyntaxError as exc:
            return [self._create_syntax_error_violation(exc, context)]

    def _create_syntax_error_violation(
        self, exc: SyntaxError, context: BaseLintContext
    ) -> Violation:
        """Create syntax error violation."""
        return Violation(
            rule_id="srp.syntax-error",
            file_path=str(context.file_path or ""),
            line=exc.lineno or 1,
            column=exc.offset or 0,
            message=f"Syntax error: {exc.msg}",
            severity=Severity.ERROR,
        )

    def _analyze_classes(
        self,
        classes: list,
        analyzer: Any,
        context: BaseLintContext,
        config: SRPConfig,
    ) -> list[Violation]:
        """Analyze classes and collect violations."""
        violations = []
        for class_node in classes:
            metrics = analyzer.analyze_class(class_node, context.file_content or "", config)
            violation = self._create_violation_if_needed(metrics, config, context)
            if violation and not self._should_ignore(violation, context):
                violations.append(violation)
        return violations

    def _check_typescript(self, context: BaseLintContext, config: SRPConfig) -> list[Violation]:
        """Check TypeScript code for SRP violations.

        Args:
            context: Lint context with file information
            config: SRP configuration

        Returns:
            List of violations found
        """
        analyzer = TypeScriptSRPAnalyzer()
        root_node = analyzer.parse_typescript(context.file_content or "")
        if not root_node:
            return []

        classes = analyzer.find_all_classes(root_node)
        return self._analyze_classes(classes, analyzer, context, config)

    def _create_violation_if_needed(
        self, metrics: dict[str, Any], config: SRPConfig, context: BaseLintContext
    ) -> Violation | None:
        """Create violation if class violates SRP thresholds.

        Args:
            metrics: Class metrics dictionary
            config: SRP configuration
            context: Lint context

        Returns:
            Violation if class violates SRP, None otherwise
        """
        issues = self._collect_srp_issues(metrics, config)
        if not issues:
            return None

        return self._build_violation(metrics, issues, context)

    def _collect_srp_issues(self, metrics: dict[str, Any], config: SRPConfig) -> list[str]:
        """Collect SRP issues for a class."""
        issues = []
        if metrics["method_count"] > config.max_methods:
            issues.append(f"{metrics['method_count']} methods (max: {config.max_methods})")
        if metrics["loc"] > config.max_loc:
            issues.append(f"{metrics['loc']} lines (max: {config.max_loc})")
        if config.check_keywords and metrics["has_keyword"]:
            issues.append("responsibility keyword in name")
        return issues

    def _build_violation(
        self, metrics: dict[str, Any], issues: list[str], context: BaseLintContext
    ) -> Violation:
        """Build violation from metrics and issues."""
        message = f"Class '{metrics['class_name']}' may violate SRP: {', '.join(issues)}"
        return Violation(
            rule_id=self.rule_id,
            file_path=str(context.file_path or ""),
            line=metrics["line"],
            column=metrics["column"],
            message=message,
            severity=Severity.ERROR,
            suggestion=self._generate_suggestion(issues),
        )

    def _generate_suggestion(self, issues: list[str]) -> str:
        """Generate refactoring suggestion based on issues."""
        suggestions = [
            self._suggest_for_methods(issues),
            self._suggest_for_lines(issues),
            self._suggest_for_keywords(issues),
        ]
        return ". ".join(filter(None, suggestions))

    def _suggest_for_methods(self, issues: list[str]) -> str:
        """Suggest fix for too many methods."""
        if any("methods" in issue for issue in issues):
            return "Consider extracting related methods into separate classes"
        return ""

    def _suggest_for_lines(self, issues: list[str]) -> str:
        """Suggest fix for too many lines."""
        if any("lines" in issue for issue in issues):
            return "Consider breaking the class into smaller, focused classes"
        return ""

    def _suggest_for_keywords(self, issues: list[str]) -> str:
        """Suggest fix for responsibility keywords."""
        if any("keyword" in issue for issue in issues):
            return "Avoid generic names like Manager, Handler, Processor"
        return ""

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

"""
Purpose: Main stateless class linter rule implementation

Scope: StatelessClassRule class implementing BaseLintRule interface

Overview: Implements stateless class linter rule following BaseLintRule interface.
    Detects Python classes that have no constructor (__init__ or __new__), no instance
    state (self.attr assignments), and 2+ methods - indicating they should be refactored
    to module-level functions. Delegates AST analysis to StatelessClassAnalyzer. Supports
    configuration via .thailint.yaml and comprehensive 5-level ignore system including
    project-level patterns, linter-specific ignore patterns, file-level directives,
    line-level directives, and block-level directives.

Dependencies: BaseLintRule, BaseLintContext, Violation, StatelessClassAnalyzer,
    IgnoreDirectiveParser, StatelessClassConfig

Exports: StatelessClassRule class

Interfaces: StatelessClassRule.check(context) -> list[Violation]

Implementation: Composition pattern delegating analysis to specialized analyzer with
    config loading and comprehensive ignore checking
"""

from pathlib import Path

from src.core.base import BaseLintContext, BaseLintRule
from src.core.types import Severity, Violation
from src.linter_config.ignore import IgnoreDirectiveParser

from .config import StatelessClassConfig
from .python_analyzer import ClassInfo, StatelessClassAnalyzer


class StatelessClassRule(BaseLintRule):  # thailint: ignore[srp,dry]
    """Detects stateless classes that should be module-level functions."""

    def __init__(self) -> None:
        """Initialize the rule with analyzer and ignore parser."""
        self._ignore_parser = IgnoreDirectiveParser()

    @property
    def rule_id(self) -> str:
        """Unique identifier for this rule."""
        return "stateless-class.violation"

    @property
    def rule_name(self) -> str:
        """Human-readable name for this rule."""
        return "Stateless Class Detection"

    @property
    def description(self) -> str:
        """Description of what this rule checks."""
        return "Classes without state should be refactored to module-level functions"

    def check(self, context: BaseLintContext) -> list[Violation]:
        """Check for stateless class violations.

        Args:
            context: Lint context with file information

        Returns:
            List of violations found
        """
        if not self._should_analyze(context):
            return []

        config = self._load_config(context)
        if not config.enabled:
            return []

        if self._is_file_ignored(context, config):
            return []

        if self._has_file_level_ignore(context):
            return []

        analyzer = StatelessClassAnalyzer(min_methods=config.min_methods)
        stateless_classes = analyzer.analyze(context.file_content)  # type: ignore[arg-type]

        return self._filter_ignored_violations(stateless_classes, context)

    def _should_analyze(self, context: BaseLintContext) -> bool:
        """Check if context should be analyzed.

        Args:
            context: Lint context

        Returns:
            True if should analyze
        """
        return context.language == "python" and context.file_content is not None

    def _load_config(self, context: BaseLintContext) -> StatelessClassConfig:
        """Load configuration from context.

        Args:
            context: Lint context

        Returns:
            StatelessClassConfig instance
        """
        if not hasattr(context, "config") or context.config is None:
            return StatelessClassConfig()

        config_dict = context.config
        if not isinstance(config_dict, dict):
            return StatelessClassConfig()

        # Check for stateless-class specific config
        linter_config = config_dict.get("stateless-class", config_dict)
        return StatelessClassConfig.from_dict(linter_config)

    def _is_file_ignored(self, context: BaseLintContext, config: StatelessClassConfig) -> bool:
        """Check if file matches ignore patterns.

        Args:
            context: Lint context
            config: Configuration

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

    def _has_file_level_ignore(self, context: BaseLintContext) -> bool:
        """Check if file has file-level ignore directive.

        Args:
            context: Lint context

        Returns:
            True if file should be ignored at file level
        """
        if not context.file_content:
            return False

        # Check first 10 lines for ignore-file directive
        lines = context.file_content.splitlines()[:10]
        for line in lines:
            if self._is_file_ignore_directive(line):
                return True
        return False

    def _is_file_ignore_directive(self, line: str) -> bool:
        """Check if line is a file-level ignore directive.

        Args:
            line: Line to check

        Returns:
            True if line has file-level ignore for this rule
        """
        line_lower = line.lower()
        if "thailint: ignore-file" not in line_lower:
            return False

        # Check for general ignore-file (no rule specified)
        if "ignore-file[" not in line_lower:
            return True

        # Check for rule-specific ignore
        return self._matches_rule_ignore(line_lower, "ignore-file")

    def _matches_rule_ignore(self, line: str, directive: str) -> bool:
        """Check if line matches rule-specific ignore.

        Args:
            line: Line to check (lowercase)
            directive: Directive name (ignore-file or ignore)

        Returns:
            True if ignore applies to this rule
        """
        import re

        pattern = rf"{directive}\[([^\]]+)\]"
        match = re.search(pattern, line)
        if not match:
            return False

        rules = [r.strip().lower() for r in match.group(1).split(",")]
        return any(self._rule_matches(r) for r in rules)

    def _rule_matches(self, rule_pattern: str) -> bool:
        """Check if rule pattern matches this rule.

        Args:
            rule_pattern: Rule pattern to check

        Returns:
            True if pattern matches this rule
        """
        rule_id_lower = self.rule_id.lower()
        pattern_lower = rule_pattern.lower()

        # Exact match
        if rule_id_lower == pattern_lower:
            return True

        # Prefix match: stateless-class matches stateless-class.violation
        if rule_id_lower.startswith(pattern_lower + "."):
            return True

        # Wildcard match: stateless-class.* matches stateless-class.violation
        if pattern_lower.endswith("*"):
            prefix = pattern_lower[:-1]
            return rule_id_lower.startswith(prefix)

        return False

    def _filter_ignored_violations(
        self, classes: list[ClassInfo], context: BaseLintContext
    ) -> list[Violation]:
        """Filter out violations that should be ignored.

        Args:
            classes: List of stateless classes found
            context: Lint context

        Returns:
            List of violations after filtering ignored ones
        """
        violations = []
        for info in classes:
            violation = self._create_violation(info, context)
            if not self._should_ignore_violation(violation, info, context):
                violations.append(violation)
        return violations

    def _should_ignore_violation(
        self, violation: Violation, info: ClassInfo, context: BaseLintContext
    ) -> bool:
        """Check if violation should be ignored.

        Args:
            violation: Violation to check
            info: Class info
            context: Lint context

        Returns:
            True if violation should be ignored
        """
        if not context.file_content:
            return False

        # Check using IgnoreDirectiveParser for comprehensive ignore checking
        if self._ignore_parser.should_ignore_violation(violation, context.file_content):
            return True

        # Also check inline ignore on class line
        return self._has_inline_ignore(info.line, context)

    def _has_inline_ignore(self, line_num: int, context: BaseLintContext) -> bool:
        """Check for inline ignore directive on class line.

        Args:
            line_num: Line number to check
            context: Lint context

        Returns:
            True if line has ignore directive
        """
        line = self._get_line_text(line_num, context)
        if not line:
            return False

        return self._is_ignore_directive(line.lower())

    def _get_line_text(self, line_num: int, context: BaseLintContext) -> str | None:
        """Get text of a specific line.

        Args:
            line_num: Line number (1-indexed)
            context: Lint context

        Returns:
            Line text or None if invalid
        """
        if not context.file_content:
            return None

        lines = context.file_content.splitlines()
        if line_num <= 0 or line_num > len(lines):
            return None

        return lines[line_num - 1]

    def _is_ignore_directive(self, line: str) -> bool:
        """Check if line contains ignore directive for this rule.

        Args:
            line: Line text (lowercase)

        Returns:
            True if line has applicable ignore directive
        """
        if "thailint:" not in line or "ignore" not in line:
            return False

        # General ignore (no rule specified)
        if "ignore[" not in line:
            return True

        # Rule-specific ignore
        return self._matches_rule_ignore(line, "ignore")

    def _create_violation(self, info: ClassInfo, context: BaseLintContext) -> Violation:
        """Create violation from class info.

        Args:
            info: Detected stateless class info
            context: Lint context

        Returns:
            Violation instance
        """
        message = (
            f"Class '{info.name}' has no state and should be refactored to module-level functions"
        )
        return Violation(
            rule_id=self.rule_id,
            message=message,
            file_path=str(context.file_path),
            line=info.line,
            column=info.column,
            severity=Severity.ERROR,
        )
